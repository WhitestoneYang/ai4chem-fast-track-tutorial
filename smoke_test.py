#!/usr/bin/env python3
"""Smoke test for the self-contained AI4Chem practice environment.

Run from the materials directory after activating the conda environment:

    python smoke_test.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdFingerprintGenerator, rdMolDescriptors
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw"
EXAMPLES = ROOT / "data/examples"
ESOL = RAW / "esol.csv"
BH = RAW / "buchwald_hartwig.csv"
EXAMPLE_MOLECULES = EXAMPLES / "example_molecules.csv"
RANDOM_STATE = 42
RDLogger.DisableLog("rdApp.error")

DESCRIPTOR_COLUMNS = [
    "MolWt",
    "MolLogP",
    "TPSA",
    "HBD",
    "HBA",
    "RotatableBonds",
    "RingCount",
    "AromaticRings",
    "FractionCSP3",
    "HeavyAtomCount",
]


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(mean_squared_error(y_true, y_pred) ** 0.5)


def mol_from_smiles(smiles: str):
    return Chem.MolFromSmiles(str(smiles).strip())


def scaffold_from_mol(mol) -> str:
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    return Chem.MolToSmiles(scaffold)


def descriptor_record(smiles: str) -> dict[str, float | str] | None:
    mol = mol_from_smiles(smiles)
    if mol is None:
        return None
    return {
        "MolWt": Descriptors.MolWt(mol),
        "MolLogP": Crippen.MolLogP(mol),
        "TPSA": rdMolDescriptors.CalcTPSA(mol),
        "HBD": Lipinski.NumHDonors(mol),
        "HBA": Lipinski.NumHAcceptors(mol),
        "RotatableBonds": Lipinski.NumRotatableBonds(mol),
        "RingCount": rdMolDescriptors.CalcNumRings(mol),
        "AromaticRings": rdMolDescriptors.CalcNumAromaticRings(mol),
        "FractionCSP3": rdMolDescriptors.CalcFractionCSP3(mol),
        "HeavyAtomCount": Descriptors.HeavyAtomCount(mol),
        "scaffold": scaffold_from_mol(mol),
        "canonical_smiles": Chem.MolToSmiles(mol),
    }


def featurize_esol(esol_raw: pd.DataFrame) -> pd.DataFrame:
    records = []
    for row_id, row in esol_raw.reset_index(drop=True).iterrows():
        desc = descriptor_record(row["smiles"])
        if desc is None:
            continue
        desc.update(
            {
                "row_id": row_id,
                "smiles": str(row["smiles"]).strip(),
                "logS": float(row["log solubility (mol/L)"]),
            }
        )
        records.append(desc)
    return pd.DataFrame(records)


def fingerprint_matrix(smiles: pd.Series, n_bits: int = 256) -> np.ndarray:
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=n_bits)
    matrix = np.zeros((len(smiles), n_bits), dtype=np.int8)
    for idx, smi in enumerate(smiles):
        fp = generator.GetFingerprint(mol_from_smiles(smi))
        DataStructs.ConvertToNumpyArray(fp, matrix[idx])
    return matrix


def evaluate_esol_models(esol: pd.DataFrame) -> pd.DataFrame:
    x_desc = esol[DESCRIPTOR_COLUMNS].to_numpy(dtype=float)
    x_fp = fingerprint_matrix(esol["smiles"])
    y = esol["logS"].to_numpy(dtype=float)
    indices = np.arange(len(esol))

    train_idx, test_idx = train_test_split(indices, test_size=0.2, random_state=RANDOM_STATE)
    group_split = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE)
    scaffold_train, scaffold_test = next(group_split.split(x_desc, y, groups=esol["scaffold"]))

    configs = [
        ("random", train_idx, test_idx, x_desc, "Baseline mean", DummyRegressor(strategy="mean")),
        ("random", train_idx, test_idx, x_desc, "Ridge descriptors", make_pipeline(StandardScaler(), Ridge())),
        (
            "random",
            train_idx,
            test_idx,
            x_desc,
            "RF descriptors",
            RandomForestRegressor(n_estimators=20, random_state=RANDOM_STATE, n_jobs=-1),
        ),
        (
            "random",
            train_idx,
            test_idx,
            x_fp,
            "RF fingerprint",
            RandomForestRegressor(n_estimators=20, random_state=RANDOM_STATE, n_jobs=-1),
        ),
        (
            "scaffold",
            scaffold_train,
            scaffold_test,
            x_desc,
            "RF descriptors",
            RandomForestRegressor(n_estimators=20, random_state=RANDOM_STATE, n_jobs=-1),
        ),
    ]

    rows = []
    for split_name, train, test, features, model_name, estimator in configs:
        model = clone(estimator)
        model.fit(features[train], y[train])
        rows.append(
            {
                "split": split_name,
                "model": model_name,
                "train_rmse": rmse(y[train], model.predict(features[train])),
                "test_rmse": rmse(y[test], model.predict(features[test])),
            }
        )
    return pd.DataFrame(rows)


def diverse_initial_indices(df: pd.DataFrame, columns: list[str], size: int = 8) -> list[int]:
    selected: list[int] = []
    used_values = {col: set() for col in columns}
    for idx, row in df.iterrows():
        gain = sum(row[col] not in used_values[col] for col in columns)
        if gain > 0 or len(selected) < max(2, size // 2):
            selected.append(idx)
            for col in columns:
                used_values[col].add(row[col])
        if len(selected) >= size:
            break
    return selected


def surrogate_optimization_loop(bh: pd.DataFrame, budget: int = 15, init_size: int = 6) -> float:
    bh = bh.copy()
    bh["yield"] = pd.to_numeric(bh["yield"], errors="coerce")
    bh = bh.dropna(subset=["yield"]).reset_index(drop=True)
    reaction_id = bh["reaction"].astype(str).value_counts().index[0]
    one_reaction = bh[bh["reaction"].astype(str) == str(reaction_id)].reset_index(drop=True)

    columns = ["ligand", "additive", "base", "aryl halide"]
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    x = encoder.fit_transform(one_reaction[columns].astype(str))
    y = one_reaction["yield"].to_numpy(dtype=float)

    observed = diverse_initial_indices(one_reaction, columns, size=min(init_size, len(one_reaction)))
    remaining = [idx for idx in range(len(y)) if idx not in observed]

    for _ in range(max(0, min(budget, len(y)) - len(observed))):
        model = RandomForestRegressor(n_estimators=20, random_state=RANDOM_STATE, n_jobs=-1)
        model.fit(x[observed], y[observed])
        pred = model.predict(x[remaining])
        next_idx = remaining[int(np.argmax(pred))]
        observed.append(next_idx)
        remaining.remove(next_idx)
    return float(np.max(y[observed]))


def main() -> None:
    for path in [ESOL, BH, EXAMPLE_MOLECULES]:
        if not path.exists():
            raise FileNotFoundError(f"Missing required file: {path}")

    examples = pd.read_csv(EXAMPLE_MOLECULES)
    valid_count = examples["smiles"].apply(lambda smi: mol_from_smiles(smi) is not None).sum()
    if valid_count < len(examples) - 1:
        raise RuntimeError("Too many example molecules failed RDKit parsing")
    if mol_from_smiles("C1CC") is not None:
        raise RuntimeError("Invalid SMILES sanity check unexpectedly parsed")

    esol_raw = pd.read_csv(ESOL)
    esol = featurize_esol(esol_raw)
    if len(esol) < 1100:
        raise RuntimeError(f"Unexpectedly small ESOL table: {len(esol)} rows")
    esol_for_modeling = esol.sample(n=500, random_state=RANDOM_STATE).reset_index(drop=True)

    model_results = evaluate_esol_models(esol_for_modeling)
    if model_results["test_rmse"].isna().any():
        raise RuntimeError("Model evaluation produced NaN RMSE")
    if model_results["test_rmse"].max() <= 0:
        raise RuntimeError("Model evaluation produced invalid RMSE")

    best_yield = surrogate_optimization_loop(pd.read_csv(BH))
    if not (0 <= best_yield <= 100):
        raise RuntimeError(f"Unexpected reaction yield from surrogate loop: {best_yield}")

    print(model_results.round(3).to_string(index=False))
    print(f"Buchwald-Hartwig surrogate best yield: {best_yield:.2f}")
    print("OK: smoke test completed")


if __name__ == "__main__":
    main()
