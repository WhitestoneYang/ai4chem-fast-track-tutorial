# 术语表

**SMILES**：把分子图写成字符串的线性表示。同一个分子可以有多个合法 SMILES。

**canonical SMILES**：软件解析分子图后，按固定规则输出的标准 SMILES。它适合去重，但依赖具体工具和化学标准化规则。

**descriptor**：数值分子属性，例如分子量、LogP、TPSA、氢键供体、氢键受体。

**fingerprint**：固定长度向量，用于编码分子片段或结构模式。Morgan/ECFP fingerprint 是化学信息学中的常见选择。

**Tanimoto similarity**：常用于二进制 fingerprint 的相似度。按 bit 集合写，可表示为 `|A 交 B| / |A 并 B|`。

**LogS**：以 mol/L 为单位的水溶性常用对数。`logS = -3` 表示约 `10^-3 mol/L`。

**Murcko scaffold**：由环系统和连接链构成的分子核心骨架近似。

**scaffold split**：尽量把不同 scaffold 分到 train/test 的数据划分方式，比 random split 更适合测试新骨架泛化。

**baseline**：简单参照模型或策略，例如预测训练集均值，或者随机搜索。

**RMSE**：均方根误差，`sqrt(mean((y_true - y_pred)^2))`。回归任务中越低越好。

**data leakage**：测试集信息进入训练或模型选择流程，导致分数虚高。

**applicability domain / 适用域**：模型有较充分证据支持的输入范围。

**surrogate model**：用来近似昂贵实验或模拟的模型。在反应优化中，它把反应条件映射到预测产率。

**acquisition function**：根据 surrogate 预测选择下一步实验的规则。UCB 使用预测均值加不确定性奖励。
