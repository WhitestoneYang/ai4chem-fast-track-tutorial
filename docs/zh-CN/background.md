# 背景知识

本教程只假设基础化学知识和入门 Python。目标不是覆盖所有 AI4Chem 方法，而是建立一个可靠框架：如何把化学问题转成数据问题。

## 化学对象如何成为数据

多数 notebook 把分子或反应当作表格中的一行：

- 分子可以表示为 SMILES、descriptor、fingerprint 和 scaffold。
- 反应可以表示为底物、ligand、base、additive、aryl halide 等类别变量。
- 标签可以是水溶性 `logS`、反应 yield 等实验测量值。

模型只能利用输入表示中包含的信息。如果立体化学、质子化状态、溶剂或实验协议没有记录，模型无法可靠恢复这些信息。

## Descriptor 与 Fingerprint

descriptor 是可解释的数值化学量，例如分子量、LogP、TPSA、氢键供体和受体。它适合做解释和小型 baseline。

fingerprint 是固定长度向量，用来编码结构片段。Morgan/ECFP fingerprint 常用于相似性搜索、QSAR、分子聚类和适用域估计。fingerprint 很高效，但单个位通常不如 descriptor 直观。

## 数据划分与评价

train/test split 决定模型分数能说明什么：

- random split 主要衡量相似数据分布内的插值能力。
- scaffold split 更严格，因为测试分子往往含有训练集中没见过的核心骨架。
- 如果要支持部署或未来数据的声明，需要 source split、time split 或 external test。

回归任务中，本教程使用 RMSE、MAE 和 parity plot。低 RMSE 不够，还要检查数据来源、split 类型、失败样例和化学合理性。

## 反应优化

反应优化是有限实验预算下的序贯决策问题。本教程比较 random search 和基于 Random Forest / Gaussian Process 的 surrogate loop。模型可以建议实验，但化学约束和实验安全判断仍然必要。
