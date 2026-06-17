# ESOL Data Card

## Source

Delaney, J. S. ESOL: estimating aqueous solubility directly from molecular structure. *Journal of Chemical Information and Computer Sciences*, 2004. https://doi.org/10.1021/ci034243x

## File

`data/raw/esol.csv`

## Main Fields

- `smiles`: molecular structure as a SMILES string.
- `log solubility (mol/L)`: aqueous solubility label used as `logS` in the notebooks.

## Teaching Use

This dataset is used for:

- SMILES parsing and canonicalization.
- Descriptor calculation.
- Duplicate and scaffold inspection.
- Baseline, Ridge, and RandomForest regression.
- random split versus scaffold split reliability checks.

## Limitations

ESOL is a small classic teaching dataset. It is useful for learning molecular property prediction workflows, but it should not be treated as a deployment-grade benchmark for modern solubility modeling without additional curation, external validation, and careful label harmonization.

Keep this data card and the DOI citation when reusing or redistributing the tutorial materials.
