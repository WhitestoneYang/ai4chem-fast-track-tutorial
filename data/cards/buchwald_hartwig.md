# Buchwald-Hartwig Data Card

## Source

Ahneman, D. T.; Estrada, J. G.; Lin, S.; Dreher, S. D.; Doyle, A. G. Predicting reaction performance in C-N cross-coupling using machine learning. *Science*, 2018. https://doi.org/10.1126/science.aar5169

## File

`data/raw/buchwald_hartwig.csv`

## Main Fields

- `reaction`: reaction or substrate identity.
- `ligand`: ligand category.
- `additive`: additive category.
- `base`: base category.
- `aryl halide`: aryl halide category.
- `product`: product identifier.
- `rxn`: reaction record identifier.
- `yield`: measured reaction yield.

## Teaching Use

This dataset is used for:

- Reaction-condition table inspection.
- Categorical one-hot encoding.
- Random search baseline.
- batch surrogate optimization with Random Forest and Gaussian Process UCB.
- Comparison of random, Latin-like, and CVT-like initial designs.

## Limitations

The notebooks simulate optimization by reading outcomes from a fixed historical table. This is useful for teaching active-learning and surrogate-loop ideas, but it is not the same as performing new wet-lab experiments. Model recommendations should always be checked against chemical feasibility, safety, and experimental constraints.

Keep this data card and the DOI citation when reusing or redistributing the tutorial materials.
