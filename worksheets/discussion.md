# Discussion Questions

Use these questions after the corresponding notebooks.

## Molecules as Data

- What chemical information is captured by SMILES?
- What information is not captured unless it is explicitly recorded?
- Why can two valid SMILES strings represent the same molecule?

## Similarity

- When does Tanimoto similarity match chemical intuition?
- When can it be misleading?
- How would the result change if descriptors were used instead of fingerprints?

## Dataset Curation

- Which ESOL metadata would you want before using the data in a real project?
- What kinds of duplicate structures can inflate model scores?
- Why is scaffold split a stronger test than random split?

## Property Prediction

- What does the baseline model tell us?
- Which failure cases are chemically interesting?
- What evidence would be needed before using the model for new molecules?

## Reaction Optimization

- Why is random search a serious baseline?
- What does a surrogate model learn from one-hot reaction conditions?
- When should a chemist reject or modify a model-suggested condition?
