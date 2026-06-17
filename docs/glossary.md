# Glossary

**SMILES**: A line notation that writes a molecular graph as a string. A single molecule can have multiple valid SMILES strings.

**canonical SMILES**: A deterministic SMILES chosen by a software toolkit after parsing a molecule graph. It is useful for deduplication, but it depends on the toolkit and chemical normalization rules.

**descriptor**: A numerical molecular property such as molecular weight, LogP, TPSA, hydrogen-bond donors, or hydrogen-bond acceptors.

**fingerprint**: A fixed-length vector encoding molecular fragments or structural patterns. Morgan/ECFP fingerprints are common in cheminformatics.

**Tanimoto similarity**: A similarity score often used for binary fingerprints. For sets of active bits, it is `|A intersection B| / |A union B|`.

**LogS**: Base-10 logarithm of aqueous solubility in mol/L. For example, `logS = -3` corresponds to about `10^-3 mol/L`.

**Murcko scaffold**: A simplified molecular framework containing ring systems and linkers. It is often used to group molecules by core structure.

**scaffold split**: A train/test split that keeps scaffold groups separated where possible. It is stricter than a random split for estimating generalization to new cores.

**baseline**: A simple reference model or strategy. Examples include predicting the training-set mean or doing random search.

**RMSE**: Root mean squared error, `sqrt(mean((y_true - y_pred)^2))`. Lower is better for regression.

**data leakage**: A failure mode where information from the test set enters training or model selection, causing overoptimistic scores.

**applicability domain**: The region of input space where a model has enough evidence to make predictions responsibly.

**surrogate model**: A model trained to approximate an expensive experiment or simulation. In reaction optimization, it maps reaction conditions to predicted yield.

**acquisition function**: A rule for selecting the next experiment from surrogate predictions. UCB, for example, uses predicted mean plus an uncertainty bonus.
