# Background

This tutorial assumes only basic chemistry and introductory Python. The goal is not to cover every AI4Chem method, but to build a reliable mental model for turning chemical questions into data problems.

## Chemical Objects as Data

Most notebooks use molecules or reactions as rows in a table:

- Molecules are represented by SMILES strings, descriptors, fingerprints, and sometimes scaffolds.
- Reactions are represented by categorical choices such as substrate, ligand, base, additive, and aryl halide.
- Labels are measured quantities such as aqueous solubility (`logS`) or reaction yield.

A model can only learn from the representation it receives. If stereochemistry, protonation state, solvent, or reaction protocol is missing, the model cannot recover that information reliably.

## Descriptors and Fingerprints

A descriptor is a human-readable numerical property such as molecular weight, LogP, TPSA, hydrogen-bond donors, or hydrogen-bond acceptors. Descriptors are useful for interpretation and small baseline models.

A fingerprint is a fixed-length vector encoding structural fragments. Morgan/ECFP fingerprints are widely used for similarity search, QSAR, molecular clustering, and applicability-domain estimates. Fingerprint bits are efficient, but individual bits are often less interpretable than descriptors.

## Splits and Evaluation

Train/test splitting defines what a model score means. A train/test split is therefore part of the scientific claim, not just a software setting:

- A random split mostly measures interpolation within a similar data distribution.
- A scaffold split is stricter because test molecules tend to contain molecular cores not seen during training.
- A source, time, or external split is needed for stronger claims about deployment or future data.

For regression, this tutorial uses RMSE, MAE, and parity plots. A low RMSE is not enough: always inspect data provenance, split type, failure cases, and chemical plausibility.

## Reaction Optimization

Reaction optimization is a sequential decision problem under limited experimental budget. The tutorial compares random search with surrogate-model loops using Random Forest and Gaussian Process models. These methods suggest experiments, but chemical constraints and experimental safety remain essential.
