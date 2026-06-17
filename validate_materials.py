#!/usr/bin/env python3
"""Validate the self-contained bilingual AI4Chem teaching repository.

This script intentionally uses only the Python standard library so it can run
before the RDKit/scikit-learn environment is installed.
"""

from __future__ import annotations

import ast
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

NOTEBOOKS = [
    "00_course_map.ipynb",
    "01_molecules_as_data.ipynb",
    "02_descriptors_fingerprints_similarity.ipynb",
    "03_esol_dataset_curation.ipynb",
    "04_property_prediction.ipynb",
    "05_model_reliability.ipynb",
    "06_molecular_space.ipynb",
    "07_reaction_optimization.ipynb",
]

DOCS = [
    "setup.md",
    "background.md",
    "glossary.md",
    "cheatsheet.md",
    "references.md",
]

REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    ROOT / "LICENSE",
    *[ROOT / "docs" / name for name in DOCS],
    *[ROOT / "docs" / "zh-CN" / name for name in DOCS],
    ROOT / "environment.yml",
    ROOT / "requirements.txt",
    ROOT / "worksheet.md",
    ROOT / "worksheet.zh-CN.md",
    ROOT / "worksheets/discussion.md",
    ROOT / "worksheets/zh-CN/discussion.md",
    ROOT / "data/raw/esol.csv",
    ROOT / "data/raw/buchwald_hartwig.csv",
    ROOT / "data/examples/example_molecules.csv",
    ROOT / "data/cards/esol.md",
    ROOT / "data/cards/buchwald_hartwig.md",
    ROOT / "smoke_test.py",
    ROOT / "build_notebook.py",
    *[ROOT / "notebooks" / name for name in NOTEBOOKS],
    *[ROOT / "notebooks" / "zh-CN" / name for name in NOTEBOOKS],
]

FORBIDDEN_RUNTIME_REFERENCES = [
    ".." + "/ai4chem_course",
    "ai4chem_course" + "/notebooks",
    "raw.githubusercontent.com/schwallergroup" + "/ai4chem_course",
]

FORBIDDEN_HEAVY_DEPENDENCIES = [
    "deep" + "chem",
    "mor" + "dred",
    "xg" + "boost",
    "bo" + "torch",
    "gp" + "ytorch",
    "torch" + "_geometric",
]

ENGLISH_NOTEBOOK_HEADINGS = {
    "00_course_map.ipynb": "# 00 Course Map: Learning AI + Chemistry Practice",
    "01_molecules_as_data.ipynb": "# 01 Molecules as Data",
    "02_descriptors_fingerprints_similarity.ipynb": "# 02 Descriptors, Fingerprints, and Similarity",
    "03_esol_dataset_curation.ipynb": "# 03 ESOL Dataset Curation: Labels, Duplicates, and Scaffolds",
    "04_property_prediction.ipynb": "# 04 Molecular Property Prediction: From Baselines to Random Forests",
    "05_model_reliability.ipynb": "# 05 Model Reliability: Splits, Leakage, and Applicability Domain",
    "06_molecular_space.ipynb": "# 06 Molecular-Space Visualization: From High-Dimensional Fingerprints to a 2D Map",
    "07_reaction_optimization.ipynb": "# 07 Reaction Optimization: Buchwald-Hartwig Condition Search",
}

CHINESE_NOTEBOOK_HEADINGS = {
    "00_course_map.ipynb": "# 00 课程地图：AI+化学实践如何学习",
    "01_molecules_as_data.ipynb": "# 01 分子如何变成数据",
    "02_descriptors_fingerprints_similarity.ipynb": "# 02 描述符、fingerprint 与相似性",
    "03_esol_dataset_curation.ipynb": "# 03 ESOL 数据整理：标签、重复与 scaffold",
    "04_property_prediction.ipynb": "# 04 分子性质预测：从 baseline 到随机森林",
    "05_model_reliability.ipynb": "# 05 模型可靠性：split、泄漏与适用域",
    "06_molecular_space.ipynb": "# 06 分子空间可视化：从高维 fingerprint 到二维图",
    "07_reaction_optimization.ipynb": "# 07 反应优化入门：Buchwald-Hartwig 条件搜索",
}

REQUIRED_TERMS = [
    "SMILES",
    "canonical SMILES",
    "Tanimoto",
    "RMSE",
    "scaffold split",
    "RandomForestRegressor",
    "Buchwald-Hartwig",
    "surrogate",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def check_required_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        fail("missing required files: " + ", ".join(missing))


def check_no_temp_dirs() -> None:
    for name in ["tmp", "executed", ".conda-pkgs", "__pycache__", ".ipynb_checkpoints"]:
        matches = [path for path in ROOT.rglob(name) if path.is_dir()]
        if matches:
            rel = ", ".join(str(path.relative_to(ROOT)) for path in matches)
            fail(f"temporary/runtime directory should not be committed: {rel}")


def read_text_files() -> dict[Path, str]:
    texts: dict[Path, str] = {}
    ignored_parts = {".conda", ".home", "__pycache__", ".ipynb_checkpoints"}
    for path in ROOT.rglob("*"):
        if ignored_parts.intersection(path.parts) or not path.is_file():
            continue
        if path.suffix.lower() in {".py", ".md", ".txt", ".yml", ".yaml", ".ipynb", ".csv"}:
            try:
                texts[path] = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                fail(f"cannot read text file {path.relative_to(ROOT)}: {exc}")
    return texts


def check_no_runtime_dependency_on_source_course(texts: dict[Path, str]) -> None:
    allowed_mentions = {
        ROOT / "README.md",
        ROOT / "README.zh-CN.md",
        ROOT / "docs/references.md",
        ROOT / "docs/zh-CN/references.md",
    }
    for path, text in texts.items():
        for phrase in FORBIDDEN_RUNTIME_REFERENCES:
            if phrase in text:
                fail(f"{path.relative_to(ROOT)} still contains forbidden runtime reference: {phrase}")
        source_repo_name = "ai4chem" + "_course"
        if source_repo_name in text and path not in allowed_mentions and path != ROOT / "validate_materials.py":
            fail(f"{path.relative_to(ROOT)} mentions ai4chem_course outside README/docs references")


def check_english_main_files(texts: dict[Path, str]) -> None:
    english_paths = [
        ROOT / "README.md",
        ROOT / "worksheet.md",
        ROOT / "worksheets/discussion.md",
        *[ROOT / "docs" / name for name in DOCS],
        *[ROOT / "notebooks" / name for name in NOTEBOOKS],
    ]
    for path in english_paths:
        text = texts[path]
        allowed = text.replace("简体中文", "")
        if has_cjk(allowed):
            fail(f"English primary file contains CJK text outside language switch: {path.relative_to(ROOT)}")


def check_dependencies(texts: dict[Path, str]) -> None:
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    environment = (ROOT / "environment.yml").read_text(encoding="utf-8").lower()
    for package in [
        "rdkit",
        "pandas",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "jupyterlab",
        "ipykernel",
        "nbconvert",
    ]:
        if package not in requirements:
            fail(f"requirements.txt missing package: {package}")
        if f"{package}==" not in requirements:
            fail(f"requirements.txt should pin exact version for package: {package}")
        if f"{package}==" not in environment:
            fail(f"environment.yml should pin exact version for package: {package}")
    if "python=3.11" not in environment:
        fail("environment.yml should pin the Python minor version: python=3.11")
    for name in FORBIDDEN_HEAVY_DEPENDENCIES:
        for path, text in texts.items():
            if name in text.lower():
                fail(f"{path.relative_to(ROOT)} should not depend on {name}")


def check_csv_schema() -> None:
    expected = {
        ROOT / "data/raw/esol.csv": {"smiles", "log solubility (mol/L)"},
        ROOT / "data/raw/buchwald_hartwig.csv": {
            "reaction",
            "ligand",
            "additive",
            "base",
            "aryl halide",
            "product",
            "rxn",
            "yield",
        },
        ROOT / "data/examples/example_molecules.csv": {"name", "smiles", "note"},
    }
    for path, required_columns in expected.items():
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            rows = list(reader)
        missing = required_columns - columns
        if missing:
            fail(f"{path.relative_to(ROOT)} missing columns: {sorted(missing)}")
        if path.name == "esol.csv" and len(rows) < 1100:
            fail("ESOL data should contain at least 1100 rows")
        if path.name == "buchwald_hartwig.csv" and len(rows) < 3900:
            fail("Buchwald-Hartwig data should contain at least 3900 rows")
        if path.name == "example_molecules.csv" and len(rows) < 8:
            fail("example_molecules.csv should contain at least 8 examples")


def load_notebook(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


def check_notebook_set(directory: Path, headings: dict[str, str], language: str) -> str:
    all_sources = []
    for name in NOTEBOOKS:
        path = directory / name
        nb = load_notebook(path)
        cells = nb.get("cells")
        if not isinstance(cells, list) or len(cells) < 8:
            fail(f"{path.relative_to(ROOT)} should contain at least 8 cells")

        source = "\n".join("".join(cell.get("source", [])) for cell in cells)
        if headings[name] not in source:
            fail(f"{path.relative_to(ROOT)} missing title heading")

        if language == "en":
            if "Observation Questions" not in source or "Summary" not in source:
                fail(f"{path.relative_to(ROOT)} should include observation questions and summary")
            if has_cjk(source):
                fail(f"{path.relative_to(ROOT)} should be English primary content")
        else:
            if "观察问题" not in source or "小结" not in source:
                fail(f"{path.relative_to(ROOT)} should include observation questions and summary")
        all_sources.append(source)

        for index, cell in enumerate(cells, start=1):
            if cell.get("cell_type") != "code":
                continue
            try:
                ast.parse("".join(cell.get("source", [])))
            except SyntaxError as exc:
                fail(f"{path.relative_to(ROOT)} code cell {index} has invalid syntax: {exc}")

    return "\n".join(all_sources)


def check_notebooks() -> None:
    english_corpus = check_notebook_set(ROOT / "notebooks", ENGLISH_NOTEBOOK_HEADINGS, "en")
    chinese_corpus = check_notebook_set(ROOT / "notebooks" / "zh-CN", CHINESE_NOTEBOOK_HEADINGS, "zh")
    corpus = english_corpus + "\n" + chinese_corpus
    for term in REQUIRED_TERMS:
        if term not in corpus:
            fail(f"notebooks missing required teaching term: {term}")


def require_phrases(path: Path, phrases: list[str], label: str) -> None:
    text = path.read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            fail(f"{label} missing phrase: {phrase}")


def check_docs() -> None:
    require_phrases(
        ROOT / "README.md",
        [
            "README.zh-CN.md",
            "4h",
            "6h",
            "8h",
            "notebooks/00_course_map.ipynb",
            "2026 Tsinghua University AI for Chemistry Interdisciplinary Practice Summer Course",
            "Schwaller group",
            "schwallergroup/ai4chem_course",
            "https://doi.org/10.1021/ci034243x",
            "https://doi.org/10.1126/science.aar5169",
            "ai4chem-practice",
            "MIT License",
        ],
        "README",
    )
    require_phrases(
        ROOT / "README.zh-CN.md",
        [
            "README.md",
            "4h",
            "6h",
            "8h",
            "notebooks/zh-CN/00_course_map.ipynb",
            "2026年清华大学 AI for Chemistry 交叉实践暑期课程",
            "Schwaller group",
            "schwallergroup/ai4chem_course",
            "https://doi.org/10.1021/ci034243x",
            "https://doi.org/10.1126/science.aar5169",
            "ai4chem-practice",
            "MIT License",
        ],
        "README.zh-CN",
    )

    for prefix in [ROOT / "docs", ROOT / "docs" / "zh-CN"]:
        require_phrases(
            prefix / "setup.md",
            ["conda env create", "conda activate ai4chem-practice", "python smoke_test.py", "jupyter lab"],
            f"{prefix.relative_to(ROOT)}/setup.md",
        )
        require_phrases(
            prefix / "background.md",
            ["SMILES", "descriptor", "fingerprint", "train/test", "RMSE"],
            f"{prefix.relative_to(ROOT)}/background.md",
        )
        require_phrases(
            prefix / "references.md",
            [
                "https://www.rdkit.org/docs/GettingStartedInPython.html",
                "https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html",
                "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html",
                "https://doi.org/10.1021/ci034243x",
                "https://doi.org/10.1126/science.aar5169",
            ],
            f"{prefix.relative_to(ROOT)}/references.md",
        )

    require_phrases(
        ROOT / "docs/glossary.md",
        ["canonical SMILES", "scaffold", "surrogate", "applicability domain"],
        "docs/glossary.md",
    )
    require_phrases(
        ROOT / "docs/zh-CN/glossary.md",
        ["canonical SMILES", "scaffold", "surrogate", "适用域"],
        "docs/zh-CN/glossary.md",
    )


def main() -> None:
    check_required_files()
    check_no_temp_dirs()
    texts = read_text_files()
    check_no_runtime_dependency_on_source_course(texts)
    check_english_main_files(texts)
    check_dependencies(texts)
    check_csv_schema()
    check_notebooks()
    check_docs()
    print("OK: bilingual self-contained AI4Chem materials validated.")


if __name__ == "__main__":
    main()
