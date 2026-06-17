# AI4Chem Practice Worksheet

Name / group:

## 1. Molecular Representation

Choose one molecule and record:

- Original SMILES:
- canonical SMILES:
- Can RDKit parse it successfully?
- If not, what may have caused the parsing failure?

## 2. Descriptors and Fingerprints

Record the Tanimoto similarity between two molecules:

- Molecule A:
- Molecule B:
- Tanimoto similarity:
- Does the similarity match your chemical intuition? Why?

## 3. ESOL Property Prediction

Record one modeling result:

- Baseline test RMSE:
- RandomForest test RMSE:
- One molecule with a large error in the parity plot:
- Why might this molecule be difficult to predict?

## 4. Model Reliability

Compare random split and scaffold split:

- Which split gives a higher test RMSE?
- Why is scaffold split usually stricter?
- What is data leakage? Give one example from this tutorial.

## 5. Reaction Optimization

In the Buchwald-Hartwig dataset:

- Which variables define a reaction condition?
- What is the difference between random search and surrogate search?
- If real experiments are expensive, how would you choose the next batch of experiments?
