# 讨论问题

可在对应 notebook 之后使用。

## 分子表示

- SMILES 捕捉了哪些化学信息？
- 哪些信息必须额外记录，不能只靠 SMILES？
- 为什么两个合法 SMILES 可以表示同一个分子？

## 相似性

- 什么情况下 Tanimoto similarity 符合化学直觉？
- 什么情况下它可能误导判断？
- 如果用 descriptor 而不是 fingerprint，相似性结果会怎样变化？

## 数据整理

- 真正做项目时，ESOL 还需要哪些元数据？
- 哪些重复结构会让模型分数虚高？
- 为什么 scaffold split 比 random split 更严格？

## 性质预测

- baseline model 告诉了我们什么？
- 哪些失败样例在化学上值得进一步分析？
- 在把模型用于新分子前，还需要哪些证据？

## 反应优化

- 为什么 random search 是必须认真比较的 baseline？
- surrogate model 能从 one-hot 反应条件中学到什么？
- 什么时候化学家应该拒绝或修改模型建议的条件？
