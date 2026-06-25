# AI4Chem Basic Practice Tutorial

English | [简体中文](README.zh-CN.md)

A self-contained Jupyter tutorial for a fast first pass through AI for Chemistry. The tutorial starts from molecular representation and moves through descriptors, fingerprints, similarity, dataset curation, property prediction, model reliability, molecular-space visualization, and reaction optimization.

Originally prepared for the 2026 Tsinghua University AI for Chemistry Interdisciplinary Practice Summer Course, this repository has been reorganized as a self-contained, bilingual public tutorial for 4-8 hour fast-track learning.

The repository is designed to run offline after installation: notebooks, small teaching datasets, data cards, validation scripts, and worksheets are included in `materials/`.

## Acknowledgements and Data Sources

This tutorial is inspired by the Schwaller group open course [`schwallergroup/ai4chem_course`](https://github.com/schwallergroup/ai4chem_course). It is a compact 4-8 hour fast-track version for self-learners who want to grasp the basic AI4Chem workflow quickly. For a fuller and more systematic AI4Chem course, refer to the original Schwaller group materials.

The tutorial uses and cites the following public datasets and references:

- ESOL aqueous solubility data: Delaney, J. S. *Journal of Chemical Information and Computer Sciences*, 2004. https://doi.org/10.1021/ci034243x
- Buchwald-Hartwig C-N cross-coupling data: Ahneman, D. T.; Estrada, J. G.; Lin, S.; Dreher, S. D.; Doyle, A. G. *Science*, 2018. https://doi.org/10.1126/science.aar5169

Dataset fields, intended use, and limitations are documented in `data/cards/`. Software and literature links are summarized in `docs/references.md`.

## Learning Paths

- 4h: `00` -> `01` -> `02` -> `03` -> `04` -> `05`
- 6h: 4h path + `06_molecular_space.ipynb`
- 8h: run `notebooks/00_course_map.ipynb` through `notebooks/07_reaction_optimization.ipynb`, then complete `worksheet.md`

Chinese localized notebooks are available in `notebooks/zh-CN/`.

## Notebook Catalog

| Notebook                                         | Topic                                                      |
| ------------------------------------------------ | ---------------------------------------------------------- |
| `00_course_map.ipynb`                          | Course map: how to learn AI + chemistry practice           |
| `01_molecules_as_data.ipynb`                   | SMILES, canonical SMILES, and molecular visualization      |
| `02_descriptors_fingerprints_similarity.ipynb` | Descriptors, fingerprints, and Tanimoto similarity         |
| `03_esol_dataset_curation.ipynb`               | ESOL curation, LogS, and scaffold split                    |
| `04_property_prediction.ipynb`                 | Baselines, Ridge, RandomForest, RMSE, and parity plots     |
| `05_model_reliability.ipynb`                   | Splits, data leakage, and applicability domain             |
| `06_molecular_space.ipynb`                     | Fingerprint PCA and molecular-space visualization          |
| `07_reaction_optimization.ipynb`               | Buchwald-Hartwig reaction optimization and surrogate loops |

## Quick Start

```bash
cd materials
conda env create -f environment.yml
conda activate ai4chem-practice
jupyter lab notebooks/00_course_map.ipynb
```

See `docs/setup.md` for installation notes.

## Repository Structure

```text
materials/
├── notebooks/              # English tutorial notebooks
│   └── zh-CN/              # Chinese localized notebooks
├── data/
│   ├── raw/                # ESOL and Buchwald-Hartwig CSV files
│   ├── examples/           # Small example molecule table
│   └── cards/              # Dataset cards and provenance notes
├── docs/                   # English setup, background, glossary, cheatsheet, references
│   └── zh-CN/              # Chinese localized docs
├── worksheets/             # Discussion questions
│   └── zh-CN/              # Chinese localized discussion questions
├── worksheet.md            # English worksheet
├── worksheet.zh-CN.md      # Chinese worksheet
├── environment.yml         # Conda environment
└── requirements.txt        # pip dependencies
```


## License

Original tutorial text, code, and notebook structure in this repository are released under the MIT License; see `LICENSE`. Distributed datasets retain their original provenance and citation requirements. Keep `data/cards/` and `docs/references.md` with any reuse or redistribution.
