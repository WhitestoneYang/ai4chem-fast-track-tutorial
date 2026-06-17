# AI4Chem 实践记录表

姓名/小组：

## 1. 分子表示

选择一个分子，写下：

- 原始 SMILES：
- canonical SMILES：
- RDKit 是否能成功解析：
- 如果不能解析，你认为可能原因是什么：

## 2. descriptor 与 fingerprint

记录两个分子的 Tanimoto similarity：

- 分子 A：
- 分子 B：
- Tanimoto：
- 这个相似度是否符合你的化学直觉？为什么？

## 3. ESOL 性质预测

记录一次模型结果：

- baseline test RMSE：
- RandomForest test RMSE：
- parity plot 中误差较大的一个分子：
- 它可能为什么难预测？

## 4. 模型可靠性

比较 random split 和 scaffold split：

- 哪一个 test RMSE 更高？
- 为什么 scaffold split 通常更严格？
- 什么是 data leakage？请结合本教程给出一个例子。

## 5. 反应优化

在 Buchwald-Hartwig 数据中：

- 反应条件由哪些变量组成？
- 随机搜索和 surrogate 搜索有什么区别？
- 如果真实实验很贵，你会如何选择下一组实验？
