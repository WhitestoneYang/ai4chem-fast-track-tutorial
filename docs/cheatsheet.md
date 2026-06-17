# AI4Chem Cheatsheet

## Core Workflow

```text
chemical object -> representation -> feature table -> label -> model -> evaluation -> chemical interpretation
```

## Common RDKit Operations

```python
from rdkit import Chem
from rdkit.Chem import Draw, Descriptors, rdFingerprintGenerator

mol = Chem.MolFromSmiles("CCO")
canonical = Chem.MolToSmiles(mol)
mw = Descriptors.MolWt(mol)
generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
fp = generator.GetFingerprint(mol)
```

## Descriptor Examples

| Descriptor | Meaning |
| --- | --- |
| `MolWt` | Molecular weight |
| `MolLogP` | Octanol/water partition estimate |
| `TPSA` | Topological polar surface area |
| `HBD` / `HBA` | Hydrogen-bond donors / acceptors |
| `RotatableBonds` | Flexibility proxy |
| `AromaticRings` | Aromatic ring count |

## Fingerprint Similarity

For binary fingerprints:

```text
Tanimoto(A, B) = c / (a + b - c)
```

`a` and `b` are the numbers of active bits in each fingerprint. `c` is the number of shared active bits.

## Regression Checks

- Compare against a baseline before trusting a more complex model.
- Report test RMSE and MAE.
- Use a parity plot to inspect systematic bias.
- Inspect the worst errors chemically.
- Compare random split with a stricter scaffold split when possible.

## Reaction Optimization Checks

- Define the candidate space clearly.
- Compare every surrogate loop with random search.
- Use repeats when initialization is random.
- Track best observed yield per round.
- Treat model recommendations as hypotheses, not chemical truth.
