# AI4Chem 速查表

## 核心流程

```text
化学对象 -> 表示 -> 特征表 -> 标签 -> 模型 -> 评价 -> 化学解释
```

## 常用 RDKit 操作

```python
from rdkit import Chem
from rdkit.Chem import Draw, Descriptors, rdFingerprintGenerator

mol = Chem.MolFromSmiles("CCO")
canonical = Chem.MolToSmiles(mol)
mw = Descriptors.MolWt(mol)
generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
fp = generator.GetFingerprint(mol)
```

## Descriptor 示例

| Descriptor | 含义 |
| --- | --- |
| `MolWt` | 分子量 |
| `MolLogP` | 辛醇/水分配估计 |
| `TPSA` | 拓扑极性表面积 |
| `HBD` / `HBA` | 氢键供体 / 受体 |
| `RotatableBonds` | 柔性近似 |
| `AromaticRings` | 芳香环数量 |

## Fingerprint 相似性

对于二进制 fingerprint：

```text
Tanimoto(A, B) = c / (a + b - c)
```

`a` 和 `b` 是两个 fingerprint 中为 1 的 bit 数，`c` 是共同为 1 的 bit 数。

## 回归检查

- 信任复杂模型前，先和 baseline 比较。
- 报告 test RMSE 和 MAE。
- 用 parity plot 检查系统偏差。
- 对最大错误样例做化学解释。
- 尽量比较 random split 和更严格的 scaffold split。

## 反应优化检查

- 明确定义候选空间。
- 每个 surrogate loop 都要和 random search 比较。
- 初始化有随机性时要做 repeats。
- 记录每一轮的 best observed yield。
- 把模型建议当作假设，而不是化学事实。
