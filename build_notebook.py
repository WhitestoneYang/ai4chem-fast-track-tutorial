#!/usr/bin/env python3
"""Build the modular self-contained AI4Chem teaching notebooks."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NOTEBOOK_DIR = ROOT / "notebooks"
ZH_NOTEBOOK_DIR = NOTEBOOK_DIR / "zh-CN"


def md(source: str) -> dict:
    text = source.strip()
    return {
        "id": "md-" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:12],
        "cell_type": "markdown",
        "metadata": {},
        "source": text.splitlines(keepends=True),
    }


def code(source: str) -> dict:
    text = source.strip()
    return {
        "id": "code-" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:12],
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }


def notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ai4chem-practice)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


COMMON_PATHS = r"""
from pathlib import Path

START = Path.cwd().resolve()
for candidate in [START, *START.parents]:
    if (candidate / "data").exists() and (candidate / "notebooks").exists():
        ROOT = candidate
        break
else:
    raise FileNotFoundError(
        "Cannot find the materials root. Start Jupyter from the materials directory "
        "or from one of its subdirectories."
    )

DATA = ROOT / "data"
RAW = DATA / "raw"
EXAMPLES = DATA / "examples"
RANDOM_STATE = 42

print("materials root:", ROOT)
"""


COMMON_CHEM = r"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from rdkit import Chem, DataStructs
from rdkit.Chem import Crippen, Descriptors, Draw, Lipinski, rdFingerprintGenerator, rdMolDescriptors
from rdkit.Chem.Scaffolds import MurckoScaffold

sns.set_theme(style="whitegrid", context="notebook")


def mol_from_smiles(smiles):
    if pd.isna(smiles):
        return None
    return Chem.MolFromSmiles(str(smiles).strip())


def canonical_smiles(smiles):
    mol = mol_from_smiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol)


def scaffold_smiles(mol):
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    return Chem.MolToSmiles(scaffold)


def descriptor_record(smiles):
    mol = mol_from_smiles(smiles)
    if mol is None:
        return None
    return {
        "MolWt": Descriptors.MolWt(mol),
        "MolLogP": Crippen.MolLogP(mol),
        "TPSA": rdMolDescriptors.CalcTPSA(mol),
        "HBD": Lipinski.NumHDonors(mol),
        "HBA": Lipinski.NumHAcceptors(mol),
        "RotatableBonds": Lipinski.NumRotatableBonds(mol),
        "RingCount": rdMolDescriptors.CalcNumRings(mol),
        "AromaticRings": rdMolDescriptors.CalcNumAromaticRings(mol),
        "FractionCSP3": rdMolDescriptors.CalcFractionCSP3(mol),
        "HeavyAtomCount": Descriptors.HeavyAtomCount(mol),
        "canonical_smiles": canonical_smiles(smiles),
        "scaffold": scaffold_smiles(mol),
    }


def build_esol_features():
    raw = pd.read_csv(RAW / "esol.csv")
    rows = []
    for row_id, row in raw.reset_index(drop=True).iterrows():
        desc = descriptor_record(row["smiles"])
        if desc is None:
            continue
        desc.update(
            {
                "row_id": row_id,
                "smiles": str(row["smiles"]).strip(),
                "logS": float(row["log solubility (mol/L)"]),
            }
        )
        rows.append(desc)
    return pd.DataFrame(rows)


def fingerprint_array(smiles, n_bits=1024):
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=n_bits)
    matrix = np.zeros((len(smiles), n_bits), dtype=np.int8)
    for idx, smi in enumerate(smiles):
        fp = generator.GetFingerprint(mol_from_smiles(smi))
        DataStructs.ConvertToNumpyArray(fp, matrix[idx])
    return matrix


DESCRIPTOR_COLUMNS = [
    "MolWt",
    "MolLogP",
    "TPSA",
    "HBD",
    "HBA",
    "RotatableBonds",
    "RingCount",
    "AromaticRings",
    "FractionCSP3",
    "HeavyAtomCount",
]
"""


def course_map() -> dict:
    cells = [
        md(
            r"""
# 00 课程地图：AI+化学实践如何学习

本课程用 8 个短模块回答一个主问题：化学对象如何变成可计算、可建模、可检验的数据任务？

本教程最初为“2026年清华大学 AI for Chemistry 交叉实践暑期课程”准备，现整理为一套自给自足、双语、可公开使用的快速入门材料。

核心路线：

```text
分子/反应 -> 表示 -> 特征 -> 标签 -> 模型 -> 评价 -> 化学判断
```

应用场景包括：分子水溶性预测、结构相似性检索、模型适用域判断、分子空间可视化、反应条件优化。
这些任务看起来都在“用 AI”，但真正的共同点是：先把化学问题翻译成可追溯的数据问题。
"""
        ),
        md(
            r"""
## 直觉解释

AI4Chem 不是“把 AI 套到化学上”这么简单。每个任务都要先说清楚：

- 输入是什么：SMILES、descriptor、fingerprint、反应条件。
- 输出是什么：溶解度、产率、活性、毒性。
- 数据是否可信：单位、重复、异常值、实验误差。
- 评价是否公平：random split、scaffold split、时间划分、外部分布。

参考资源：RDKit 文档适合查分子表示和 cheminformatics 操作；scikit-learn 文档适合查模型、
split 和评价指标；Delaney ESOL 与 Ahneman/Doyle Buchwald-Hartwig 数据分别对应本课的性质预测
和反应优化主线。
"""
        ),
        md(
            r"""
## 数学/化学定义

本课程会反复使用这组符号：

```text
X: feature matrix，每一行是一个分子或反应条件
y: label vector，例如 logS 或 yield
f(X): model prediction
error = y_true - y_pred
```

模型不是化学定律。模型只是从有限数据中学到的近似函数。
"""
        ),
        code(COMMON_PATHS),
        code(
            r"""
import pandas as pd

# 这一格只做 inventory：确认本课程自带哪些数据文件，以及每个文件服务哪个教学任务。
examples = pd.read_csv(EXAMPLES / "example_molecules.csv")
esol = pd.read_csv(RAW / "esol.csv")
bh = pd.read_csv(RAW / "buchwald_hartwig.csv")

summary = pd.DataFrame(
    [
        {"file": "example_molecules.csv", "rows": len(examples), "main_use": "SMILES and molecule display"},
        {"file": "esol.csv", "rows": len(esol), "main_use": "solubility prediction"},
        {"file": "buchwald_hartwig.csv", "rows": len(bh), "main_use": "reaction optimization"},
    ]
)
summary
"""
        ),
        md(
            r"""
## 代码

下面用一张表把完整材料拆成模块。时间有限时，可先完成 `00` 到 `05`。
"""
        ),
        code(
            r"""
modules = pd.DataFrame(
    [
        ["00", "课程地图", "知道任务框架和学习路线"],
        ["01", "分子如何变成数据", "会读 SMILES、canonical SMILES、分子图"],
        ["02", "描述符与 fingerprint", "理解 descriptor、Morgan fingerprint、Tanimoto"],
        ["03", "ESOL 数据整理", "知道标签、重复、scaffold 和 provenance"],
        ["04", "性质预测", "训练 baseline、Ridge、RandomForestRegressor"],
        ["05", "模型可靠性", "比较 random split 和 scaffold split"],
        ["06", "分子空间", "用 PCA 看高维 fingerprint 的二维投影"],
        ["07", "反应优化", "用 Buchwald-Hartwig 数据理解 surrogate 搜索"],
    ],
    columns=["编号", "主题", "学习目标"],
)
modules
"""
        ),
        md(
            r"""
## 观察问题

1. 你最熟悉的是哪类输入：分子结构、反应条件、图像、光谱，还是文本？
2. 如果一个模型在测试集 RMSE 很低，它一定能指导真实化学实验吗？
3. 你认为“数据集来源”和“划分方式”哪个更容易被初学者忽略？

### Hints

1. 可以从你最熟悉的化学课内容出发：有机结构式更接近分子图，分析化学数据更接近光谱/图像，实验设计更接近反应条件表。
2. 不一定。要先问测试集是否真的代表未来要预测的分子、反应或实验条件。
3. 两者都容易被忽略。来源决定标签是否可信，划分方式决定模型分数能支持多强的泛化声明。
"""
        ),
        md(
            r"""
## 小结

本课程的目标不是训练最强模型，而是让你能看懂一个 AI4Chem 工作流：数据从哪里来、分子如何编码、模型如何预测、评价为什么可能误导、结果如何回到化学判断。
"""
        ),
    ]
    return notebook(cells)


def molecules_as_data() -> dict:
    cells = [
        md(
            r"""
# 01 分子如何变成数据

这一节从 SMILES 开始。SMILES 是 **Simplified Molecular Input Line Entry System** 的缩写，
是一种把分子图写成一行字符串的表示方法。它适合存储、检索、放进表格，也适合作为后续
descriptor、fingerprint 和机器学习模型的起点。

应用场景：化学数据库检索、结构去重、虚拟筛选、性质预测、反应 SMILES 表示。
经典出处可追溯到 Weininger 提出的 SMILES 表示；实际使用时以 RDKit/Daylight 等工具的解析规则为准。
"""
        ),
        md(
            r"""
## 直觉解释

SMILES 可以理解为“沿着分子图走一遍，并把路线上遇到的原子、键、分支、环闭合写下来”。
因为同一个分子图可以从不同原子开始走，也可以选择不同方向和不同分支顺序，所以同一个分子
常常有多种合法 SMILES 写法。

例子：乙醇可以写成 `CCO`，也可以写成 `OCC`。它们对应同一个分子图。

为了去重和比较，我们常把输入 SMILES 转换成 canonical SMILES。canonical SMILES 的意思是：
软件先解析出分子图，再用固定的排序和遍历规则选出一种标准写法。只要分子图、同位素、
电荷、芳香性、立体化学等信息被同一个工具以同样规则理解，输出就应该是确定的。
"""
        ),
        code(COMMON_PATHS),
        code(
            r"""
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw
from IPython.display import display

# 这一格先读取示例分子表。后面每个分子都会被 RDKit 解析成 molecule object。
examples = pd.read_csv(EXAMPLES / "example_molecules.csv")
examples
"""
        ),
        md(
            r"""
## 数学/化学定义

分子图可以看作：

```text
G = (V, E)
V: atoms
E: bonds
```

SMILES 是这个图的一种线性写法，不是唯一写法。canonical SMILES 是算法选择的一种标准线性写法。

需要注意：canonical SMILES 的“唯一”是实践中的唯一，不是脱离软件和化学约定的绝对唯一。
如果没有明确立体化学、质子化状态、盐形式、互变异构体或原子映射，两个字符串仍然可能代表
本教程范围之外更复杂的化学差异。
"""
        ),
        code(
            r"""
def parse_status(smiles):
    # MolFromSmiles 会把字符串解析成 RDKit 分子图；解析失败时返回 None。
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return pd.Series({"valid": False, "canonical SMILES": None, "atoms": None, "bonds": None})
    return pd.Series(
        {
            "valid": True,
            "canonical SMILES": Chem.MolToSmiles(mol),
            "atoms": mol.GetNumAtoms(),
            "bonds": mol.GetNumBonds(),
        }
    )

parsed = pd.concat([examples, examples["smiles"].apply(parse_status)], axis=1)
parsed
"""
        ),
        md(
            r"""
## 代码

RDKit 可以把 SMILES 解析成分子对象，再画出二维结构。无效 SMILES 会返回 `None`。
"""
        ),
        code(
            r"""
valid = parsed[parsed["valid"]].copy()
mols = [Chem.MolFromSmiles(smi) for smi in valid["smiles"]]
legends = [f"{name}\n{can}" for name, can in zip(valid["name"], valid["canonical SMILES"])]

# SVG 是矢量图，放大后仍然清晰；subImgSize 越大，legend 中的 SMILES 越容易读。
Draw.MolsToGridImage(mols, molsPerRow=3, subImgSize=(360, 260), legends=legends, useSVG=True)
"""
        ),
        code(
            r"""
student_smiles = "CC(=O)Oc1ccccc1C(=O)O"  # try replacing this with your molecule
mol = Chem.MolFromSmiles(student_smiles)

if mol is None:
    print("RDKit cannot parse this SMILES.")
else:
    print("canonical SMILES:", Chem.MolToSmiles(mol))
    print("atoms:", mol.GetNumAtoms(), "bonds:", mol.GetNumBonds())

    mol_with_labels = Chem.Mol(mol)
    for atom in mol_with_labels.GetAtoms():
        atom.SetProp("atomNote", f"{atom.GetSymbol()}{atom.GetIdx()}")

    display(
        Draw.MolsToGridImage(
            [mol_with_labels],
            molsPerRow=1,
            subImgSize=(520, 380),
            legends=["atom labels show element symbol + atom index"],
            useSVG=True,
        )
    )
"""
        ),
        md(
            r"""
## 观察问题

1. `CCO` 和 `OCC` 的 canonical SMILES 是否相同？
2. `invalid_ring` 为什么不能被 RDKit 解析？
3. canonical SMILES 解决了什么问题？它没有解决什么问题？

### Hints

1. 先让 RDKit 分别解析 `CCO` 和 `OCC`，再比较 `Chem.MolToSmiles(...)` 的输出。
2. 无效 SMILES 常见原因包括环编号没有闭合、括号不匹配、原子价态不合理、非法字符等。
3. canonical SMILES 主要解决“同一个分子有多种字符串写法”导致的去重和比较问题；它不能自动解决
   互变异构体、质子化状态、盐形式、构象、溶剂和实验条件这些化学语境问题。
"""
        ),
        md(
            r"""
## 小结

SMILES 让分子可以进入表格和代码；canonical SMILES 让去重更容易。但 SMILES 本身不等于全部化学信息，例如实验条件、构象、溶剂和测量误差仍然需要额外记录。
"""
        ),
    ]
    return notebook(cells)


def descriptors_similarity() -> dict:
    cells = [
        md(
            r"""
# 02 描述符、fingerprint 与相似性

这一节把分子转成模型能处理的数字：descriptor 和 fingerprint。我们会先看 descriptor 表，
再介绍 fingerprint，最后用 fingerprint 计算 Tanimoto similarity。

应用场景：相似性搜索、虚拟筛选、QSAR 建模、分子聚类、适用域估计。
本节的 Morgan/ECFP 思路可参考 Rogers 和 Hahn 对 extended-connectivity fingerprints 的介绍；
具体 RDKit 用法以 RDKit fingerprint generator 文档为准。
"""
        ),
        md(
            r"""
## 直觉解释

descriptor 像“分子简历”：分子量、LogP、TPSA、氢键供体/受体。fingerprint 像“结构片段清单”：某些局部结构出现就把对应位置标为 1。

这两类表示回答的问题不同：

- descriptor 更适合解释“这个分子有什么整体性质”，例如大不大、极不极性、氢键多不多。
- fingerprint 更适合比较“这两个分子是否含有相似的局部结构片段”。

在本教程中，Tanimoto similarity 通常基于 fingerprint 计算，不直接基于少数 descriptor。
数学上，Tanimoto/Jaccard 可以推广到非负向量；但如果用 MolWt、LogP、
TPSA 这类 descriptor 比较分子，通常会先标准化，再用 Euclidean distance、cosine similarity、
Mahalanobis distance 或机器学习模型中的距离/核函数。否则不同量纲会让结果很难解释。
"""
        ),
        md(
            r"""
## Fingerprint 是什么

Fingerprint 是把分子结构编码成一个固定长度向量。最常见的是二进制 fingerprint：

```text
bit = 1: 某个结构片段出现过
bit = 0: 这个结构片段没有出现
```

本教程使用 Morgan fingerprint。它会从每个原子出发，逐层扩展局部环境；`radius=2` 大致表示
考虑每个原子周围两层键以内的局部结构。常见 fingerprint 还包括：

| Fingerprint | 直觉 | 常见用途 |
| --- | --- | --- |
| Morgan/ECFP | 原子周围的圆形局部环境 | 相似性搜索、QSAR、虚拟筛选 |
| MACCS keys | 一组预定义结构问题，例如是否有某类官能团 | 快速教学、可解释的结构筛选 |
| RDKit topological fingerprint | 沿分子图路径枚举片段 | 通用相似性搜索 |
| Atom-pair fingerprint | 记录原子对类型和拓扑距离 | 关注远距离结构关系 |
| Pharmacophore fingerprint | 编码药效团特征和空间/拓扑关系 | 药物发现中的相似性 |

不同 fingerprint 会让“相似”的含义发生变化。因此相似性不是分子的绝对属性，而是“表示方法 + 相似性公式”的结果。
"""
        ),
        md(
            r"""
## 数学/化学定义

Tanimoto similarity 衡量两个 fingerprint 的重叠：

```text
T(A, B) = c / (a + b - c)
```

`a` 是 A 中为 1 的 bit 数，`b` 是 B 中为 1 的 bit 数，`c` 是 A 和 B 同时为 1 的 bit 数。

如果把 fingerprint 看成两个集合：

```text
A = molecule A 中出现的结构片段集合
B = molecule B 中出现的结构片段集合

T(A, B) = |A ∩ B| / |A ∪ B|
```

这就是集合版本的 Jaccard similarity；在化学信息学里常称为 Tanimoto similarity。它这样定义的直觉是：
分子越相似，共有片段占“两个分子总共出现过的片段”的比例越高。

和其他相似性/距离的简单比较：

| 方法 | 形式/直觉 | 适合什么 | 局限 |
| --- | --- | --- | --- |
| Tanimoto/Jaccard | 共有片段 / 总片段 | 稀疏二进制 fingerprint | 不告诉你片段是否同等重要；受 fingerprint 选择影响 |
| Dice similarity | `2c / (a + b)`，更强调共有部分 | 二进制集合比较 | 往往比 Tanimoto 数值更高，不同文献不可直接混用 |
| Cosine similarity | 向量夹角 | 连续向量、embedding、计数向量 | 对二进制 fingerprint 可用，但化学检索默认较少用 |
| Euclidean distance | 几何距离 | 标准化后的 descriptor 表 | 对量纲敏感；高维稀疏 bit 上直觉较弱 |

优势：Tanimoto 对稀疏 fingerprint 简单、快速、范围固定在 0 到 1，适合相似性搜索。
缺点：它只看 bit 的重叠，不知道哪个片段更关键，也不直接表达构象、反应条件、实验误差或机制。
"""
        ),
        code(COMMON_PATHS),
        code(COMMON_CHEM),
        code(
            r"""
examples = pd.read_csv(EXAMPLES / "example_molecules.csv")
examples = examples[examples["smiles"].apply(lambda s: mol_from_smiles(s) is not None)].reset_index(drop=True)

# 这一格把每个示例分子的 SMILES 转成一组容易解释的 descriptor。
# 先看 descriptor 表，是为了把“分子变成数字”这件事落到可读的化学量上。
descriptor_rows = []
for _, row in examples.iterrows():
    desc = descriptor_record(row["smiles"])
    desc.update({"name": row["name"], "smiles": row["smiles"]})
    descriptor_rows.append(desc)

desc_table = pd.DataFrame(descriptor_rows)
desc_table[["name", "MolWt", "MolLogP", "TPSA", "HBD", "HBA", "RingCount", "canonical_smiles"]].round(2)
"""
        ),
        md(
            r"""
## 代码

下面计算 Morgan fingerprint 和两两 Tanimoto similarity。相似度越接近 1，表示 fingerprint 重叠越多。

读代码时抓住三步：

1. 用 `GetMorganGenerator(radius=2, fpSize=1024)` 定义 fingerprint 规则。
2. 把每个 SMILES 转成 fingerprint。
3. 用 RDKit 的 `FingerprintSimilarity` 计算两两 Tanimoto similarity。
"""
        ),
        code(
            r"""
# radius 控制看多大的局部环境，fpSize 控制压缩到多少个 bit。
generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
fps = [generator.GetFingerprint(mol_from_smiles(smi)) for smi in examples["smiles"]]

# sim[i, j] 是第 i 个分子和第 j 个分子的 Tanimoto similarity。
sim = np.zeros((len(fps), len(fps)))
for i, fp_i in enumerate(fps):
    for j, fp_j in enumerate(fps):
        sim[i, j] = DataStructs.FingerprintSimilarity(fp_i, fp_j)

sim_df = pd.DataFrame(sim, index=examples["name"], columns=examples["name"])
sim_df.round(2)
"""
        ),
        code(
            r"""
# 热图把相似性矩阵画出来；对角线一定是 1，因为每个分子和自己完全相同。
plt.figure(figsize=(8, 6))
sns.heatmap(sim_df, vmin=0, vmax=1, cmap="viridis", annot=True, fmt=".2f")
plt.title("Tanimoto similarity from Morgan fingerprints")
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
"""
        ),
        code(
            r"""
pair = ("benzene", "toluene")  # try ("ethanol", "glucose") or ("aspirin", "ibuprofen")
idx_a = examples.index[examples["name"] == pair[0]][0]
idx_b = examples.index[examples["name"] == pair[1]][0]

# 改 pair 可以快速检查“数值相似性”和你的化学直觉是否一致。
print(pair, "Tanimoto =", sim[idx_a, idx_b].round(3))
Draw.MolsToGridImage(
    [mol_from_smiles(examples.loc[idx_a, "smiles"]), mol_from_smiles(examples.loc[idx_b, "smiles"])],
    legends=list(pair),
    subImgSize=(260, 200),
)
"""
        ),
        md(
            r"""
## 观察问题

1. benzene 和 toluene 的相似度是否符合直觉？
2. descriptor 表中，哪个指标最容易和水溶性联系起来？
3. fingerprint 位本身不直观，为什么仍然有用？

### Hints

1. benzene 和 toluene 共享芳香环，Tanimoto 应该比较高；但 methyl 取代会引入额外片段，所以不会等于 1。
2. 可以先看 `MolLogP`、`TPSA`、`HBD`、`HBA`。水溶性常和极性、氢键能力、疏水性有关，但不会由单个 descriptor 完全决定。
3. fingerprint 的单个位不容易解释，但整组 bit 能高效表达大量局部结构片段，因此适合相似性搜索和机器学习输入。
"""
        ),
        md(
            r"""
## 小结

descriptor 更容易解释，fingerprint 更适合捕捉局部结构。Tanimoto similarity 是基于 fingerprint 的相似性指标，不等于“真实化学相似性”的全部。
"""
        ),
    ]
    return notebook(cells)


def esol_curation() -> dict:
    cells = [
        md(
            r"""
# 03 ESOL 数据整理：标签、重复与 scaffold

这一节把 ESOL 数据当成一个真实数据集检查，而不是直接扔给模型。重点是：
标签 `logS` 到底是什么意思、数据从哪里来、派生特征如何可追溯，以及不同 split 会支持什么样的模型声明。
"""
        ),
        md(
            r"""
## 直觉解释

AI4Chem 的第一步不是模型，而是数据。要先问：

- 标签是什么单位？
- 数据来自哪篇论文或哪个数据库？
- SMILES 能否解析？
- 是否有重复结构或近似重复结构？
- 测试集是否和训练集太像？

ESOL 是一个经典的小型水溶性数据集，常用于教学 molecular property prediction。它适合练习
descriptor、fingerprint、baseline、random split 和 scaffold split，但它不是现代部署级水溶性 benchmark。
"""
        ),
        md(
            r"""
## 数学/化学定义

ESOL 的标签是 `log solubility (mol/L)`，本课记为 `logS`：

```text
S: aqueous solubility，单位 mol/L
logS = log10(S / (1 mol/L))
```

例如 `logS = -3` 表示溶解度约为 `10^-3 mol/L`。因为很多有机小分子的水溶性低于 1 mol/L，
所以 logS 常常是负数。

本课程使用的 ESOL 数据来自 Delaney 的水溶性数据集：

> Delaney, J. S. ESOL: estimating aqueous solubility directly from molecular structure.
> Journal of Chemical Information and Computer Sciences, 2004. DOI: 10.1021/ci034243x

scaffold 是分子核心骨架的一种近似。scaffold split 会尽量让训练集和测试集包含不同骨架，
用于更严格地估计模型对新结构核心的外推能力。
"""
        ),
        md(
            r"""
## Split hierarchy：数据划分决定能支持什么声明

数据划分不是技术细节，而是在定义“模型到底学会了什么”。粗略说：

| split | 怎么划分 | 支持的结论 | 不能说明什么 |
| --- | --- | --- | --- |
| random split | 随机抽一部分做测试集 | 对同一数据分布内相似分子的插值能力 | 不能说明能外推到新骨架 |
| scaffold split | 按 Murcko scaffold 分组，让测试骨架尽量没在训练集中出现 | 对新核心骨架的初步外推能力 | 仍可能有近邻泄漏；不能说明来源/时间外推 |
| cluster split | 先按 fingerprint similarity 聚类，再按簇划分 | 比 scaffold 更直接控制结构相似度 | 聚类阈值会影响结论 |
| source split | 按实验来源、实验室、论文或 assay 分组 | 对不同实验来源/协议的鲁棒性 | ESOL 这份 CSV 缺少足够来源元数据 |
| time split | 按发表年份或数据进入数据库的时间切分 | 更接近未来部署 | 需要可靠时间戳；本课数据不具备 |
| external test | 用完全独立数据集测试 | 最接近真实泛化检查 | 成本高，且要确认标签定义一致 |

一句话：random split 只能支持“在相似数据中的插值表现”；如果要说模型能预测新骨架、新实验来源或未来数据，
就需要更强的 split 或外部测试集。本节先检查 ESOL 的结构和 scaffold 分布，后面 `04` 会做 random split 建模，
`05` 会比较 random split 和 scaffold split。
"""
        ),
        md(
            r"""
## 准备路径

这一格只负责找到 `materials/` 根目录和 `data/` 路径。这样无论从 `materials/` 还是 `notebooks/`
目录打开 notebook，后续读数据的路径都一致。
"""
        ),
        code(COMMON_PATHS),
        md(
            r"""
## 准备 RDKit 工具函数

这一格定义本课程反复使用的函数：解析 SMILES、生成 canonical SMILES、计算 descriptor、
提取 Murcko scaffold，并把 ESOL 原始表转换成建模前的派生表。
"""
        ),
        code(COMMON_CHEM),
        md(
            r"""
## 读取 raw ESOL

先只看原始 CSV 的行数、列名和前几行。这里不做任何覆盖式修改，是为了保留 raw data 的可追溯性。
"""
        ),
        code(
            r"""
# raw 只包含 SMILES 和实验标签；派生列会在后面新建，不直接写回 raw CSV。
raw = pd.read_csv(RAW / "esol.csv")
print(raw.shape)
raw.head()
"""
        ),
        md(
            r"""
## 创建可追溯派生表

下面创建可追溯的派生表：保留原始行号，新增 canonical SMILES、descriptor 和 scaffold，不覆盖 raw CSV。
"""
        ),
        code(
            r"""
# build_esol_features 会跳过 RDKit 不能解析的 SMILES，并保留原始 row_id。
esol = build_esol_features()

print("raw rows:", len(raw))
print("valid molecule rows:", len(esol))
print("invalid rows:", len(raw) - len(esol))
esol[["row_id", "smiles", "canonical_smiles", "scaffold", "logS"]].head()
"""
        ),
        md(
            r"""
## 检查重复结构

同一个分子可能有多种 SMILES 写法。用 canonical SMILES 分组可以发现 identity leakage 风险：
如果同一结构同时出现在 train 和 test，测试分数会被高估。
"""
        ),
        code(
            r"""
# canonical_smiles 相同，说明 RDKit 认为它们是同一个标准化后的分子图。
duplicate_counts = esol["canonical_smiles"].value_counts()
num_duplicate_structures = int((duplicate_counts > 1).sum())
print("duplicated canonical structures:", num_duplicate_structures)

if num_duplicate_structures:
    duplicated = esol[esol["canonical_smiles"].isin(duplicate_counts[duplicate_counts > 1].index)]
    display(duplicated.sort_values("canonical_smiles").head(10))
else:
    print("No duplicate canonical SMILES found.")
"""
        ),
        md(
            r"""
## 查看标签分布和简单趋势

这两张图回答两个基础问题：`logS` 的范围大概在哪里？分子量和水溶性有没有粗略关系？
这不是建模结论，只是帮助我们理解标签和明显异常点。
"""
        ),
        code(
            r"""
# 左图看标签分布，右图看一个简单 descriptor 与标签的关系。
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.histplot(esol["logS"], bins=35, ax=axes[0])
axes[0].set_title("ESOL label distribution")
axes[0].set_xlabel("logS")

sns.scatterplot(data=esol, x="MolWt", y="logS", alpha=0.6, ax=axes[1])
axes[1].set_title("Molecular weight vs logS")
plt.tight_layout()
"""
        ),
        md(
            r"""
## 查看 scaffold 分布

scaffold 分布会影响后续 split。若某个 scaffold 占比很高，random split 很可能让相似骨架同时出现在
训练集和测试集；scaffold split 则会更接近“测试新核心结构”的问题。
"""
        ),
        code(
            r"""
# 空 scaffold 常见于无环分子；这里把它显示成更容易读的标签。
scaffold_summary = (
    esol["scaffold"]
    .replace("", "[no ring scaffold]")
    .value_counts()
    .head(10)
    .rename_axis("scaffold")
    .reset_index(name="count")
)
scaffold_summary
"""
        ),
        md(
            r"""
## 观察问题

1. ESOL 的 logS 大致分布在哪个范围？
2. 分子量和溶解度之间是否有明显趋势？有哪些例外？
3. 为什么 data card 要说明来源、单位和限制？

### Hints

1. 看 histogram 的横轴范围；多数分子 logS 为负，说明摩尔溶解度低于 1 mol/L。
2. 分子量越大通常越不易溶，但这只是弱趋势。含多个氢键供体/受体、带强极性基团或离子化状态的分子可能偏离这个趋势。
3. 来源、单位和限制决定标签是否可比较。没有 data card，就很难判断模型学到的是水溶性规律、实验来源偏差，还是数据整理过程中的偶然模式。
"""
        ),
        md(
            r"""
## 小结

数据整理不是“清洗脏数据”这么简单，而是建立可追溯的证据链。raw 数据要保留，派生特征要可复现，重复和 scaffold 会影响后续模型评价。
"""
        ),
    ]
    return notebook(cells)


def property_prediction() -> dict:
    cells = [
        md(
            r"""
# 04 分子性质预测：从 baseline 到随机森林

这一节用 ESOL 做回归任务：输入分子特征，预测 logS。

应用场景：在合成、药物发现或材料筛选中，先用已有数据估计候选分子的性质，再决定哪些分子值得进一步实验。
本节使用 scikit-learn 的 `DummyRegressor`、`Ridge` 和 `RandomForestRegressor` 做轻量比较；数据仍来自 Delaney ESOL。
"""
        ),
        md(
            r"""
## 直觉解释

建模前先做 baseline。baseline 回答：“如果模型什么结构都不学，只预测训练集均值，表现如何？”任何复杂模型都应该和 baseline 比。

化学解释上，baseline 是“没有利用结构信息”的参照；Ridge 尝试用 descriptor 的线性组合解释 logS；
RandomForest 可以捕捉非线性关系，但也更容易在小数据上记住局部模式。
"""
        ),
        md(
            r"""
## 数学/化学定义

RMSE：

```text
RMSE = sqrt(mean((y_true - y_pred)^2))
```

MAE：

```text
MAE = mean(abs(y_true - y_pred))
```

parity plot：横轴真实值，纵轴预测值；点越接近对角线，预测越准。
"""
        ),
        md(
            r"""
## 准备数据和模型工具

这一部分读取 ESOL 派生特征，把 descriptor 表变成 `X`，把 logS 变成 `y`，并做一个 random train/test split。
注意：random split 只是在这一数据分布内做插值评估，不能证明模型能外推到新骨架。
"""
        ),
        code(COMMON_PATHS),
        code(COMMON_CHEM),
        code(
            r"""
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# X 是分子 descriptor 矩阵；y 是实验 logS 标签。
esol = build_esol_features()
X = esol[DESCRIPTOR_COLUMNS].to_numpy(dtype=float)
y = esol["logS"].to_numpy(dtype=float)

# 这里先用 random split 训练入门模型；更严格的 scaffold split 放到下一章。
train_idx, test_idx = train_test_split(np.arange(len(esol)), test_size=0.2, random_state=RANDOM_STATE)
print(len(train_idx), "train rows;", len(test_idx), "test rows")
"""
        ),
        md(
            r"""
## 代码

比较三个模型：均值 baseline、线性 Ridge、RandomForestRegressor。
"""
        ),
        code(
            r"""
models = {
    "Baseline mean": DummyRegressor(strategy="mean"),
    "Ridge descriptors": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
    "RandomForest descriptors": RandomForestRegressor(n_estimators=60, random_state=RANDOM_STATE, n_jobs=-1),
}

rows = []
predictions = {}
for name, estimator in models.items():
    # clone 确保每个模型都是未训练的新实例，避免上一个模型状态泄漏。
    model = clone(estimator)
    model.fit(X[train_idx], y[train_idx])
    pred_train = model.predict(X[train_idx])
    pred_test = model.predict(X[test_idx])
    predictions[name] = pred_test
    rows.append(
        {
            "model": name,
            "train_RMSE": mean_squared_error(y[train_idx], pred_train) ** 0.5,
            "test_RMSE": mean_squared_error(y[test_idx], pred_test) ** 0.5,
            "test_MAE": mean_absolute_error(y[test_idx], pred_test),
            "test_R2": r2_score(y[test_idx], pred_test),
        }
    )

results = pd.DataFrame(rows).sort_values("test_RMSE")
results.round(3)
"""
        ),
        md(
            r"""
## 读 parity plot

这一格选择 test RMSE 最低的模型，画出真实 logS 与预测 logS。对角线不是拟合线，
而是“完美预测线”；偏离越远，误差越大。
"""
        ),
        code(
            r"""
best_name = results.iloc[0]["model"]
plot_df = pd.DataFrame(
    {
        "true_logS": y[test_idx],
        "pred_logS": predictions[best_name],
        "smiles": esol.iloc[test_idx]["smiles"].to_numpy(),
    }
)

plt.figure(figsize=(5, 5))
sns.scatterplot(data=plot_df, x="true_logS", y="pred_logS", alpha=0.7)
lims = [min(plot_df["true_logS"].min(), plot_df["pred_logS"].min()), max(plot_df["true_logS"].max(), plot_df["pred_logS"].max())]
plt.plot(lims, lims, "k--", linewidth=1)
plt.title(f"Parity plot: {best_name}")
plt.tight_layout()
"""
        ),
        md(
            r"""
## 找最难预测的分子

模型平均分数只能告诉我们整体误差。还需要检查失败样例：
它们是否更大、更疏水、官能团特殊，或者落在训练集中少见的结构区域？
"""
        ),
        code(
            r"""
# abs_error 帮我们找到这次 test split 中预测偏差最大的分子。
plot_df["abs_error"] = (plot_df["true_logS"] - plot_df["pred_logS"]).abs()
worst = plot_df.sort_values("abs_error", ascending=False).head(6)
display(worst[["true_logS", "pred_logS", "abs_error", "smiles"]].round(3))

Draw.MolsToGridImage(
    [mol_from_smiles(s) for s in worst["smiles"]],
    legends=[f"err={e:.2f}" for e in worst["abs_error"]],
    molsPerRow=3,
    subImgSize=(260, 180),
)
"""
        ),
        md(
            r"""
## 观察问题

1. RandomForestRegressor 是否一定比 Ridge 好？
2. train RMSE 和 test RMSE 差很多时，可能意味着什么？
3. 最差预测样例有什么共同结构或 descriptor 特征？

### Hints

1. 不一定。RandomForest 能表达非线性，但在小数据、弱特征或分布外测试时不保证更好。
2. train 很低、test 明显更高通常提示过拟合，或者测试集和训练集分布不同。
3. 可以回到 descriptor 表看 MolWt、MolLogP、TPSA、HBD/HBA，也可以观察是否有大环、多个杂原子、强疏水片段或训练集中少见结构。
"""
        ),
        md(
            r"""
## 小结

性质预测要先建立 baseline，再比较模型。RMSE 和 parity plot 是读懂回归结果的起点，但它们还不能回答模型是否能外推到新骨架。
"""
        ),
    ]
    return notebook(cells)


def model_reliability() -> dict:
    cells = [
        md(
            r"""
# 05 模型可靠性：split、泄漏与适用域

这一节讨论一个更科学的问题：模型在什么情况下可信？

应用场景：当模型要给新分子排序、筛选候选或建议实验时，单个 random-split 分数不够。
我们需要知道测试分子是否只是训练集近邻，或者是否真的代表新的化学结构空间。
"""
        ),
        md(
            r"""
## 直觉解释

如果测试集里有许多训练集近邻，模型看起来会很好。scaffold split 更像“考新题”，random split 更像“同一题型换数字”。

本节使用 Murcko scaffold 近似“分子核心骨架”。Bemis 和 Murcko 提出的 molecular framework 思路
常用于把分子按核心骨架分组；在机器学习评估中，scaffold split 常作为比 random split 更严格的结构外推检查。
"""
        ),
        md(
            r"""
## 数学/化学定义

data leakage 指测试信息进入训练流程。适用域指模型比较有证据支持的输入范围。

一种简单适用域指标：

```text
nearest_train_similarity(test molecule) = max Tanimoto(test, each train molecule)
```

相似度越低，模型越可能是在分布外预测。
"""
        ),
        md(
            r"""
## 准备 random split 和 scaffold split

这一格建立同一份 ESOL 特征，然后生成两种划分：

- random split：随机抽测试集，通常测试插值能力。
- scaffold split：按 scaffold 分组抽测试集，测试集核心骨架更可能没在训练集中出现。
"""
        ),
        code(COMMON_PATHS),
        code(COMMON_CHEM),
        code(
            r"""
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupShuffleSplit, train_test_split

esol = build_esol_features()
X = esol[DESCRIPTOR_COLUMNS].to_numpy(dtype=float)
y = esol["logS"].to_numpy(dtype=float)
indices = np.arange(len(esol))

# random split 不关心化学骨架，只随机抽样。
random_train, random_test = train_test_split(indices, test_size=0.2, random_state=RANDOM_STATE)

# GroupShuffleSplit 保证同一个 scaffold group 不会同时进入 train/test。
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE)
scaffold_train, scaffold_test = next(splitter.split(X, y, groups=esol["scaffold"]))
"""
        ),
        md(
            r"""
## 代码

用同一个模型比较 random split 和 scaffold split。差异越大，越说明评价依赖划分方式。
"""
        ),
        code(
            r"""
def fit_and_score(train_idx, test_idx):
    # 固定模型，只改变 split；这样差异主要来自评价设置，而不是模型选择。
    model = RandomForestRegressor(n_estimators=60, random_state=RANDOM_STATE, n_jobs=-1)
    model.fit(X[train_idx], y[train_idx])
    pred_train = model.predict(X[train_idx])
    pred_test = model.predict(X[test_idx])
    return {
        "train_RMSE": mean_squared_error(y[train_idx], pred_train) ** 0.5,
        "test_RMSE": mean_squared_error(y[test_idx], pred_test) ** 0.5,
        "pred_test": pred_test,
    }

scores = {
    "random split": fit_and_score(random_train, random_test),
    "scaffold split": fit_and_score(scaffold_train, scaffold_test),
}

pd.DataFrame(
    [
        {"split": name, "train_RMSE": value["train_RMSE"], "test_RMSE": value["test_RMSE"]}
        for name, value in scores.items()
    ]
).round(3)
"""
        ),
        md(
            r"""
## 用最近训练邻居估计适用域

对每个测试分子，计算它和所有训练分子的 Morgan fingerprint Tanimoto similarity，
取最大值作为 `nearest_train_similarity`。这不是严格不确定性，但能提供一个直观的适用域 proxy。
"""
        ),
        code(
            r"""
def nearest_train_similarity(train_idx, test_idx):
    all_fp = []
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
    for smi in esol["smiles"]:
        all_fp.append(generator.GetFingerprint(mol_from_smiles(smi)))
    out = []
    train_fps = [all_fp[i] for i in train_idx]
    for idx in test_idx:
        # BulkTanimotoSimilarity 一次计算当前测试分子和所有训练分子的相似度。
        sims = DataStructs.BulkTanimotoSimilarity(all_fp[idx], train_fps)
        out.append(max(sims))
    return np.array(out)

random_nn = nearest_train_similarity(random_train, random_test)
scaffold_nn = nearest_train_similarity(scaffold_train, scaffold_test)

sim_df = pd.DataFrame(
    {
        "nearest_train_similarity": np.r_[random_nn, scaffold_nn],
        "split": ["random split"] * len(random_nn) + ["scaffold split"] * len(scaffold_nn),
    }
)

plt.figure(figsize=(7, 4))
sns.histplot(data=sim_df, x="nearest_train_similarity", hue="split", bins=25, element="step", stat="density", common_norm=False)
plt.title("Applicability domain proxy: nearest training similarity")
plt.tight_layout()
"""
        ),
        md(
            r"""
## 找低相似度和高错误样例

这一格把 scaffold split 的预测误差和最近邻相似度放在同一张表里。
讨论时可以问：这些分子是模型真的不会，还是训练集里缺少相似化学环境？
"""
        ),
        code(
            r"""
reliability_df = pd.DataFrame(
    {
        "true_logS": y[scaffold_test],
        "pred_logS": scores["scaffold split"]["pred_test"],
        "nearest_train_similarity": scaffold_nn,
        "smiles": esol.iloc[scaffold_test]["smiles"].to_numpy(),
    }
)
reliability_df["abs_error"] = (reliability_df["true_logS"] - reliability_df["pred_logS"]).abs()
reliability_df.sort_values(["nearest_train_similarity", "abs_error"], ascending=[True, False]).head(8).round(3)
"""
        ),
        md(
            r"""
## 可视化风险关系

横轴越低，表示测试分子离训练集越远；纵轴越高，表示预测误差越大。
如果看到低相似度区域错误更大，就应该把模型输出当作假设，而不是确定结论。
"""
        ),
        code(
            r"""
plt.figure(figsize=(6, 4))
sns.scatterplot(data=reliability_df, x="nearest_train_similarity", y="abs_error", alpha=0.7)
plt.title("Low similarity often means higher risk")
plt.tight_layout()
"""
        ),
        md(
            r"""
## 观察问题

1. random split 和 scaffold split 的 test RMSE 哪个更高？
2. scaffold split 的测试分子和训练集最近邻相似度是否更低？
3. 如果一个分子 nearest similarity 很低，你会如何使用模型预测？

### Hints

1. 通常 scaffold split 更高，但要看这次随机种子和数据分布；关键是解释为什么。
2. 如果 scaffold split 成功制造了结构外推，最近邻相似度分布应该整体更低。
3. 低相似度预测更适合作为“需要进一步验证的假设”。可以要求实验确认、查找外部相似数据，或让模型 abstain。
"""
        ),
        md(
            r"""
## 小结

模型可靠性不是只看一个分数。要同时看 split、重复、近邻相似性、错误样例和化学解释。对于低相似度样本，预测应被视为假设，而不是结论。
"""
        ),
    ]
    return notebook(cells)


def molecular_space() -> dict:
    cells = [
        md(
            r"""
# 06 分子空间可视化：从高维 fingerprint 到二维图

这一节把 fingerprint 从高维投影到二维，帮助观察分子空间。

应用场景：检查数据覆盖范围、发现离群分子、观察性质梯度、为主动学习或实验设计提供直觉。
本节用 scikit-learn 的 PCA 做最基础的线性降维；它适合教学，但不能替代严格的相似性/外推评价。
"""
        ),
        md(
            r"""
## 直觉解释

每个分子可以看成 fingerprint 空间中的一个点。相似分子通常更近，但二维图只是投影，会丢失信息。

化学上，这张图可以帮助我们问：疏水分子是否聚在一起？高分子量分子是否在某一区域？
logS 是否呈现连续变化？如果没有清晰区域，也不代表模型没用，可能只是二维投影不足以表达高维结构。
"""
        ),
        md(
            r"""
## 数学/化学定义

PCA 寻找方差最大的方向，把高维矩阵 `X` 投影到少数主成分：

```text
X_high_dim -> PC1, PC2
```

PCA 不知道化学规则，只根据数值方差工作。
"""
        ),
        md(
            r"""
## 准备 PCA 输入

这一格从 ESOL 中抽样，计算 Morgan fingerprint，再用 PCA 压缩到二维。
`explained_variance_ratio_` 表示 PC1/PC2 保留了多少数值方差信息；它通常不会很高，因为 fingerprint 很高维且稀疏。
"""
        ),
        code(COMMON_PATHS),
        code(COMMON_CHEM),
        code(
            r"""
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

esol = build_esol_features()

# 为了运行快，只抽取最多 600 个分子；random_state 保证每次结果可复现。
sample = esol.sample(n=min(600, len(esol)), random_state=RANDOM_STATE).reset_index(drop=True)
fp = fingerprint_array(sample["smiles"], n_bits=384)

# PCA 只看 fingerprint 矩阵的数值方差，不知道 logS 或化学机制。
pca = PCA(n_components=2, random_state=RANDOM_STATE)
coords = pca.fit_transform(fp)

space = sample[["smiles", "logS", "MolWt", "MolLogP", "TPSA"]].copy()
space["PC1"] = coords[:, 0]
space["PC2"] = coords[:, 1]
print("explained variance ratio:", pca.explained_variance_ratio_.round(3))
space.head()
"""
        ),
        md(
            r"""
## 代码

下面用颜色表示 logS。观察空间位置是否与溶解度、分子量或 LogP 有关系。
"""
        ),
        code(
            r"""
# 如果颜色形成连续区域，说明二维投影捕捉到一部分和 logS 相关的结构差异。
plt.figure(figsize=(7, 5))
scatter = plt.scatter(space["PC1"], space["PC2"], c=space["logS"], cmap="coolwarm", s=24, alpha=0.8)
plt.colorbar(scatter, label="logS")
plt.title("PCA of Morgan fingerprints")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.tight_layout()
"""
        ),
        md(
            r"""
## 换 descriptor 给点上色

同一张二维坐标可以用不同化学量上色。

区分的概念：“空间位置由 fingerprint 决定”，而“颜色只是我们叠加上去帮助解释的属性”。
"""
        ),
        code(
            r"""
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.scatterplot(data=space, x="PC1", y="PC2", hue="MolWt", palette="viridis", ax=axes[0], legend=False)
axes[0].set_title("Colored by MolWt")
sns.scatterplot(data=space, x="PC1", y="PC2", hue="MolLogP", palette="magma", ax=axes[1], legend=False)
axes[1].set_title("Colored by MolLogP")
plt.tight_layout()
"""
        ),
        md(
            r"""
## 看投影边缘的分子

这一格抽出 PC1/PC2 极端位置的分子。边缘点常常帮助解释 PCA 方向可能对应哪些结构差异，
但不要把 PC1/PC2 直接解释成单一化学性质。
"""
        ),
        code(
            r"""
# 取 PC1/PC2 两端的分子，看看二维图边缘到底是什么结构。
extreme = pd.concat(
    [
        space.nsmallest(3, "PC1"),
        space.nlargest(3, "PC1"),
        space.nsmallest(3, "PC2"),
        space.nlargest(3, "PC2"),
    ]
).drop_duplicates().head(12)

Draw.MolsToGridImage(
    [mol_from_smiles(s) for s in extreme["smiles"]],
    legends=[f"logS={v:.1f}" for v in extreme["logS"]],
    molsPerRow=4,
    subImgSize=(230, 170),
)
"""
        ),
        md(
            r"""
## 观察问题

1. PCA 图上相邻分子一定化学相似吗？
2. logS 的颜色是否形成清晰区域？
3. 高维 fingerprint 投影到二维会丢失哪些信息？

### Hints

1. 不一定。二维邻近只说明在 PC1/PC2 上接近；高维 fingerprint 中的差异可能被压缩掉。
2. 如果颜色有梯度，说明某些结构差异和 logS 相关；如果颜色混杂，可能说明 logS 受多种因素影响或投影不足。
3. 会丢失局部结构 bit、稀有片段、非线性关系和高维邻居关系。二维图适合提出问题，不适合作为最终证据。
"""
        ),
        md(
            r"""
## 小结

分子空间图适合建立直觉、找异常点和讲故事，但不能替代严格评价。二维距离只是高维结构的一种压缩结果。
"""
        ),
    ]
    return notebook(cells)


def reaction_optimization() -> dict:
    cells = [
        md(
            r"""
# 07 反应优化入门：Buchwald-Hartwig 条件搜索

本节使用真实 Buchwald-Hartwig 数据，说明反应优化为什么是一个“有限预算下的序贯决策”问题。

应用场景：真实实验昂贵时，化学家希望在有限预算内尽快找到高产率条件。
本节数据来自 Ahneman、Estrada、Lin、Dreher 和 Doyle 关于 C-N cross-coupling 反应性能预测的 Science 2018 工作。

Reference:

- Ahneman, D. T.; Estrada, J. G.; Lin, S.; Dreher, S. D.; Doyle, A. G. Predicting reaction performance in C-N cross-coupling using machine learning. Science, 2018, 360, 186-190.
"""
        ),
        md(
            r"""
## 直觉解释

反应产率受底物、ligand、base、additive、aryl halide 等条件影响。
真实实验预算有限，因此我们希望用少量已观察实验训练 surrogate model，建议下一组更可能高产率的条件。

化学解释上，ligand 影响金属中心电子/空间环境，base 和 additive 影响反应路径和副反应，
aryl halide 改变底物反应性。模型只能从已有表格中学习这些关联，不能自动保证建议条件有机制合理性。
"""
        ),
        md(
            r"""
## 数学/化学定义

简单优化循环：

```text
1. 先观察少量实验 D = {(condition_i, yield_i)}
2. 训练 surrogate: condition -> yield
3. acquisition 选择下一组未做条件
4. 读取或执行该实验，更新 D
```

本节比较三类策略：

1. random search: 不学习，只随机抽条件。
2. Random Forest greedy: 用 one-hot 条件训练 RF surrogate，只选预测均值最高的条件。
3. Gaussian Process UCB: 用 GP surrogate 同时利用预测均值和不确定性，选择 `mean + beta * std` 最大的条件。

为了更接近实际高通量实验，本节使用 batch optimization：每轮一次选择 5 个候选条件，等这一批结果都观察到之后再训练下一轮模型。

包括三种初始设计：

- random initial design: 第一批随机选 5 个条件。
- Latin-like level coverage: 在离散条件空间中尽量覆盖每个因子的不同水平，类似 LHC 想覆盖各维度的思想。
- CVT-like/maximin: 在 one-hot 空间中贪心选择彼此尽量远的点，类似 CVT/space-filling design 的覆盖思想。

注意：严格的 LHC 和 CVT 主要用于连续变量空间。这里的反应条件是离散类别变量，所以使用的是面向类别空间的近似版本。

因此图中会有 7 条主要曲线：1 条 random baseline，加上 `3 initial designs × 2 surrogate models`。
每条曲线都跑 10 个 repeat，用均值和 10-90% 区间显示，避免把单次随机种子的偶然结果当成结论。
"""
        ),
        md(
            r"""
## 读取 Buchwald-Hartwig 数据

这一格读取反应条件表并把 yield 转成数值。每一行是一个已测过的条件组合；
模拟会从固定数据表中“读取结果”，不是真正执行新的湿实验。
"""
        ),
        code(COMMON_PATHS),
        code(
            r"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, DotProduct, WhiteKernel
from sklearn.preprocessing import OneHotEncoder

sns.set_theme(style="whitegrid", context="notebook")

# 原始表中每行是一组 reaction + ligand/base/additive/aryl halide 条件和对应 yield。
bh = pd.read_csv(RAW / "buchwald_hartwig.csv")
bh["yield"] = pd.to_numeric(bh["yield"], errors="coerce")
bh = bh.dropna(subset=["yield"]).reset_index(drop=True)
print(bh.shape)
bh.head()
"""
        ),
        md(
            r"""
## 定义完整候选空间

`reaction` 表示底物/反应身份，ligand、additive、base、aryl halide 表示可选反应条件。
如果同一个条件组合有重复记录，这里取平均 yield，避免同一实验重复影响优化轨迹。
"""
        ),
        code(
            r"""
condition_columns = ["reaction", "ligand", "additive", "base", "aryl halide"]

bh_conditions = bh[condition_columns + ["yield"]].dropna().copy()
for col in condition_columns:
    bh_conditions[col] = bh_conditions[col].astype(str)

# 一个候选点就是 reaction + 条件组合；重复测量时用平均产率表示该候选点。
candidate_df = (
    bh_conditions
    .groupby(condition_columns, as_index=False, sort=False)["yield"]
    .mean()
    .reset_index(drop=True)
)

# 统计每类条件有多少种选择，用于量化组合空间为什么很快变大。
space_summary = pd.DataFrame(
    {
        "condition": condition_columns,
        "unique_choices": [candidate_df[col].nunique() for col in condition_columns],
    }
)
estimated_factorial = int(np.prod(space_summary["unique_choices"]))
print("realized candidate rows:", len(candidate_df))
print("full factorial combinations if fully crossed:", f"{estimated_factorial:,}")
space_summary
"""
        ),
        md(
            r"""
## 查看产率分布

如果高产率条件很少，随机搜索需要较大预算才有机会撞到好条件；
如果高产率条件很多，随机搜索也可能表现不错。
"""
        ),
        code(
            r"""
plt.figure(figsize=(7, 4))
sns.histplot(candidate_df["yield"], bins=30)
plt.xlabel("yield")
plt.title("Buchwald-Hartwig yield distribution across realized candidates")
plt.tight_layout()
"""
        ),
        md(
            r"""
## 高产率条件到底稀不稀有？

如果高产率条件并不稀有，random search 是很强的 baseline；这也是很多优化论文必须认真报告随机基线的原因。
下面先看不同产率阈值以上的候选比例。
"""
        ),
        code(
            r"""
y_all = candidate_df["yield"].to_numpy(dtype=float)
thresholds = [40, 50, 60, 70, 80]

pd.DataFrame(
    {
        "yield_threshold": thresholds,
        "fraction_of_candidates_at_or_above": [(y_all >= t).mean() for t in thresholds],
        "count": [(y_all >= t).sum() for t in thresholds],
    }
)
"""
        ),
        md(
            r"""
## 编码反应条件

scikit-learn 模型不能直接处理字符串类别。one-hot encoding 会把每个类别水平变成一个 0/1 特征：
例如某一行是否使用了某个 ligand、某个 base、某个 reaction id。

这是一种很朴素的表示。它能表达“某个条件是否出现”，但不会显式表达配位化学、电子效应或底物结构相似性。
"""
        ),
        code(
            r"""
encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
X_all = encoder.fit_transform(candidate_df[condition_columns].astype(str))
y_all = candidate_df["yield"].to_numpy(dtype=float)

print("X shape:", X_all.shape)
print("yield range:", f"{y_all.min():.1f} to {y_all.max():.1f}")
candidate_df.nlargest(5, "yield")[condition_columns + ["yield"]]
"""
        ),
        md(
            r"""
## 定义随机搜索和初始设计

反应优化中，前几组实验通常不是随便选的：需要尽量覆盖不同 ligand、base、additive 或底物类型。
下面几个函数分别给出 batch random baseline、random/Latin-like/CVT-like 初始化。
"""
        ),
        code(
            r"""
def batch_best_trace(yields, observed_order, batch_size=5):
    # 在每个 batch 完成后记录“目前见过的最好产率”。
    observed_order = list(map(int, observed_order))
    counts = []
    best_values = []
    for end in range(batch_size, len(observed_order) + 1, batch_size):
        counts.append(end)
        best_values.append(float(np.max(yields[observed_order[:end]])))

    # 如果最后一个 batch 不满 batch_size，也记录最终结果。
    if counts and counts[-1] != len(observed_order):
        counts.append(len(observed_order))
        best_values.append(float(np.max(yields[observed_order])))
    elif not counts and observed_order:
        counts.append(len(observed_order))
        best_values.append(float(np.max(yields[observed_order])))

    return np.asarray(counts), np.asarray(best_values)


def simulate_random_batches(yields, budget=40, batch_size=5, repeats=200, seed=RANDOM_STATE):
    # Baseline: 每一轮随机选 batch_size 个未观察候选；下一轮仍然随机，不训练模型。
    # 这个过程只利用 observed set 来避免重复选择，不利用 observed yield 来指导下一轮。
    rng = np.random.default_rng(seed)
    traces = []
    n = len(yields)
    budget = min(budget, n)
    for _ in range(repeats):
        order = rng.choice(n, size=budget, replace=False)
        _, trace = batch_best_trace(yields, order, batch_size=batch_size)
        traces.append(trace)
    return np.asarray(traces)


def random_initial_indices(total_size, size=5, seed=RANDOM_STATE):
    # 初始 batch 的随机设计。
    rng = np.random.default_rng(seed)
    return list(map(int, rng.choice(total_size, size=min(size, total_size), replace=False)))


def latin_like_initial_indices(df, columns, size=8, seed=RANDOM_STATE):
    # 离散版“Latin-like”初始化：每一步优先选择能覆盖更多未见类别水平的候选。
    rng = np.random.default_rng(seed)
    selected = []
    used_values = {col: set() for col in columns}
    pool = list(rng.permutation(len(df)))

    while len(selected) < min(size, len(df)) and pool:
        gains = []
        for idx in pool:
            row = df.iloc[idx]
            gains.append(sum(row[col] not in used_values[col] for col in columns))

        # gain 相同的时候随机打破平局，避免总是受原始表顺序影响。
        best_gain = max(gains)
        tied_positions = [pos for pos, gain in enumerate(gains) if gain == best_gain]
        chosen_position = int(rng.choice(tied_positions))
        idx = int(pool.pop(chosen_position))
        selected.append(idx)
        for col in columns:
            used_values[col].add(df.iloc[idx][col])

    return selected


def maximin_initial_indices(X, size=8, seed=RANDOM_STATE):
    # CVT-like / space-filling 思路：在 one-hot 空间中贪心选择离已有点最远的候选。
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    size = min(size, n)
    first = int(rng.integers(n))
    selected = [first]
    min_dist = np.full(n, np.inf)

    while len(selected) < size:
        last = selected[-1]
        diff = X - X[last]
        dist = np.sqrt(np.einsum("ij,ij->i", diff, diff))
        min_dist = np.minimum(min_dist, dist)
        min_dist[selected] = -np.inf
        selected.append(int(np.argmax(min_dist)))

    return selected
"""
        ),
        md(
            r"""
## 定义 surrogate 优化循环

RF greedy 只看预测均值，容易过早 exploitation。
GP-UCB 使用预测均值和不确定性，形式是：

```text
acquisition(x) = mean(x) + beta * std(x)
```

`beta` 越大，越鼓励探索模型不确定的区域。

这里每一轮选择一个 batch 的候选点。注意：同一个 batch 中的 5 个点是同时选择的，
不会因为第 1 个点结果很好就立刻改变第 2-5 个点。
"""
        ),
        code(
            r"""
def _prepare_observed(init_indices, total_size, limit):
    # 去重并保证初始化数量不超过 batch size、预算和候选数量。
    observed = []
    for idx in init_indices:
        idx = int(idx)
        if idx not in observed:
            observed.append(idx)
        if len(observed) >= min(total_size, limit):
            break
    return observed


def _take_top_k(remaining, scores, k):
    # 从 remaining 中取 acquisition score 最高的 k 个候选，作为下一批实验。
    order = np.argsort(scores)[::-1][:k]
    return [remaining[int(pos)] for pos in order]


def run_rf_batch_greedy(X, y, init_indices, budget=40, batch_size=5, seed=RANDOM_STATE):
    observed = _prepare_observed(init_indices, len(y), min(batch_size, budget))
    remaining = [idx for idx in range(len(y)) if idx not in observed]

    while len(observed) < min(budget, len(y)) and remaining:
        model = RandomForestRegressor(
            n_estimators=60,
            min_samples_leaf=2,
            random_state=seed,
            n_jobs=-1,
        )
        model.fit(X[observed], y[observed])
        predicted_mean = model.predict(X[remaining])

        # Greedy acquisition: 每轮一次性选择预测均值最高的一批候选。
        k = min(batch_size, budget - len(observed), len(remaining))
        next_batch = _take_top_k(remaining, predicted_mean, k)
        observed.extend(next_batch)
        remaining = [idx for idx in remaining if idx not in set(next_batch)]
    counts, trace = batch_best_trace(y, observed, batch_size=batch_size)
    return counts, trace, observed


def run_gp_batch_ucb(X, y, init_indices, budget=40, batch_size=5, beta=1.5, seed=RANDOM_STATE):
    observed = _prepare_observed(init_indices, len(y), min(batch_size, budget))
    remaining = [idx for idx in range(len(y)) if idx not in observed]

    while len(observed) < min(budget, len(y)) and remaining:
        # DotProduct kernel 在 one-hot 类别特征上相当于学习线性相似性；
        # WhiteKernel 表示观测噪声。这里关闭超参数优化，使运行更快、更稳定。
        kernel = ConstantKernel(1.0) * DotProduct(sigma_0=1.0) + WhiteKernel(noise_level=1.0)
        model = GaussianProcessRegressor(
            kernel=kernel,
            normalize_y=True,
            alpha=1e-6,
            optimizer=None,
            random_state=seed,
        )
        model.fit(X[observed], y[observed])
        predicted_mean, predicted_std = model.predict(X[remaining], return_std=True)

        # UCB acquisition: exploitation + exploration。
        acquisition = predicted_mean + beta * predicted_std
        k = min(batch_size, budget - len(observed), len(remaining))
        next_batch = _take_top_k(remaining, acquisition, k)
        observed.extend(next_batch)
        remaining = [idx for idx in remaining if idx not in set(next_batch)]
    counts, trace = batch_best_trace(y, observed, batch_size=batch_size)
    return counts, trace, observed
"""
        ),
        md(
            r"""
## 比较搜索策略

曲线表示每一轮 batch 完成后，当前已经观察到的最好产率。黑色虚线是这个固定数据表中的全局最好值；
真实实验中我们通常不知道这条线在哪里。

这里的 random baseline 是“每轮随机选 5 个未做条件，下一轮仍然随机”。它不训练模型，
但会避免重复选择同一个候选。surrogate 方法则是先用 random/Latin-like/CVT-like 选第一批 5 个点，
之后每轮用 RF 或 GP-UCB 选择下一批 5 个点。

为了避免偶然性，每个策略跑 10 个 repeat。横轴显示 round：round 1 是第一批 5 个实验完成后，
round 20 对应总共 100 个实验完成后。

如果 random search 和 surrogate 很接近，可能有几个原因：

1. 候选空间不大，预算占比不低。
2. 高产率候选在空间里并不稀有。
3. one-hot 类别特征很粗糙，RF/GP 不能真正理解反应机理。
4. 小数据早期 surrogate 很不稳定；没有足够观测时，模型建议未必优于随机。
"""
        ),
        code(
            r"""
batch_size = 5
n_rounds = 20
n_repeats = 10
budget = min(batch_size * n_rounds, len(candidate_df))
actual_rounds = int(np.ceil(budget / batch_size))
round_steps = np.arange(1, actual_rounds + 1)

def make_initial_design(design_name, seed):
    if design_name == "random init":
        return random_initial_indices(len(candidate_df), size=batch_size, seed=seed)
    if design_name == "Latin-like init":
        return latin_like_initial_indices(candidate_df, condition_columns, size=batch_size, seed=seed)
    if design_name == "CVT-like init":
        return maximin_initial_indices(X_all, size=batch_size, seed=seed)
    raise ValueError(f"unknown initial design: {design_name}")

initial_design_names = ["random init", "Latin-like init", "CVT-like init"]
random_traces = simulate_random_batches(
    y_all,
    budget=budget,
    batch_size=batch_size,
    repeats=n_repeats,
    seed=RANDOM_STATE,
)

method_results = {}
for design_name in initial_design_names:
    rf_traces = []
    rf_observed_runs = []
    gp_traces = []
    gp_observed_runs = []

    for repeat in range(n_repeats):
        seed = RANDOM_STATE + repeat
        init_indices = make_initial_design(design_name, seed)

        _, trace, observed = run_rf_batch_greedy(
            X_all, y_all, init_indices, budget=budget, batch_size=batch_size, seed=seed
        )
        rf_traces.append(trace)
        rf_observed_runs.append(observed)

        _, trace, observed = run_gp_batch_ucb(
            X_all, y_all, init_indices, budget=budget, batch_size=batch_size, beta=1.5, seed=seed
        )
        gp_traces.append(trace)
        gp_observed_runs.append(observed)

    rf_traces = np.asarray(rf_traces)
    gp_traces = np.asarray(gp_traces)
    rf_best_run = int(np.argmax(rf_traces[:, -1]))
    gp_best_run = int(np.argmax(gp_traces[:, -1]))

    method_results[f"RF + {design_name}"] = {
        "model": "RF greedy",
        "initial_design": design_name,
        "traces": rf_traces,
        "best_observed": rf_observed_runs[rf_best_run],
    }

    method_results[f"GP-UCB + {design_name}"] = {
        "model": "GP-UCB",
        "initial_design": design_name,
        "traces": gp_traces,
        "best_observed": gp_observed_runs[gp_best_run],
    }

plt.figure(figsize=(9, 5))
plt.plot(round_steps, random_traces.mean(axis=0), label="random baseline", linewidth=2.5, color="black")
plt.fill_between(
    round_steps,
    np.percentile(random_traces, 10, axis=0),
    np.percentile(random_traces, 90, axis=0),
    color="black",
    alpha=0.12,
    label="random 10-90%",
)

for label, result in method_results.items():
    linestyle = "--" if result["model"] == "RF greedy" else "-"
    traces = result["traces"]
    mean_trace = traces.mean(axis=0)
    p10 = np.percentile(traces, 10, axis=0)
    p90 = np.percentile(traces, 90, axis=0)
    line, = plt.plot(round_steps, mean_trace, label=label, linewidth=2, linestyle=linestyle)
    plt.fill_between(round_steps, p10, p90, color=line.get_color(), alpha=0.08)

plt.axhline(y_all.max(), linestyle="--", color="black", linewidth=1, label="best in dataset")
plt.xlabel("optimization round")
plt.ylabel("best yield observed so far")
plt.title(f"Batch reaction optimization: {batch_size} experiments/round, {n_repeats} repeats")
plt.xticks(round_steps)
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
"""
        ),
        md(
            r"""
## 数值汇总

把随机搜索和 6 个 surrogate 组合在 10 个 repeat 中的最终最好值放在一起。
这里的重点不是证明某个方法永远更好，而是学会用 mean 和 uncertainty band 判断 surrogate loop 到底有没有带来增益。

如果单次运行中 `RF + random init` 最好，不一定说明它稳定优于 GP 或 space-filling init。
RF 对 one-hot 离散类别表格通常很强；GP-UCB 的不确定性在高维稀疏 one-hot 空间中也可能校准不好。
因此需要看 10 次 repeat 的平均表现和 10-90% 区间。
"""
        ),
        code(
            r"""
random_final = random_traces[:, -1]

summary_rows = [
    {
        "method": "random baseline",
        "initial_design": "random every batch",
        "mean_best_yield_after_20_rounds": random_final.mean(),
        "p10": np.percentile(random_final, 10),
        "p90": np.percentile(random_final, 90),
        "best_repeat": random_final.max(),
    }
]

for label, result in method_results.items():
    final_values = result["traces"][:, -1]
    summary_rows.append(
        {
            "method": result["model"],
            "initial_design": result["initial_design"],
            "mean_best_yield_after_20_rounds": final_values.mean(),
            "p10": np.percentile(final_values, 10),
            "p90": np.percentile(final_values, 90),
            "best_repeat": final_values.max(),
        }
    )

method_summary = pd.DataFrame(summary_rows).sort_values("mean_best_yield_after_20_rounds", ascending=False)
method_summary
"""
        ),
        md(
            r"""
## 查看 surrogate 实际观察到的好条件

最后列出 6 个 surrogate 组合各自 best repeat 中观察过的最高产率条件。分析重点不是“模型赢了没有”，
而是这些条件是否有化学合理性，以及如果真实实验昂贵，下一步是否还需要探索多样性。
"""
        ),
        code(
            r"""
def best_observed_conditions(method_label, observed, top=3):
    out = candidate_df.iloc[observed].copy()
    out["order"] = np.arange(1, len(out) + 1)
    out["method"] = method_label
    return out.sort_values("yield", ascending=False).head(top)[["method", "order", *condition_columns, "yield"]]


pd.concat(
    [best_observed_conditions(label, result["best_observed"]) for label, result in method_results.items()],
    ignore_index=True,
)
"""
        ),
        md(
            r"""
## 观察问题

1. 为什么只固定一个 reaction id 时，surrogate loop 可能和 random search 差不多？
2. batch size = 5 时，为什么同一个 batch 内不能用第一个点的结果更新后四个点？
3. RF greedy 和 GP-UCB 的 acquisition 有什么本质差别？
4. LHC/CVT 这类 space-filling design 为什么在连续变量中更自然？离散反应条件中应该怎么解释？
5. 如果单次运行中 `RF + random init` 最好，应该怎样判断这是偶然还是稳定优势？
6. 如果模型建议的条件不符合化学常识，应该相信模型还是重新检查数据和假设？

### Hints

1. 固定 reaction id 后空间很小；如果高产率条件比例不低，random 很容易撞到好条件。RF 早期数据少、one-hot 表示粗糙，也不一定能学出可靠规律。
2. batch 实验是并行提交的一组实验；只有整批完成后才知道产率，所以同一批次中不能序贯更新模型。
3. RF greedy 只利用预测均值，倾向 exploitation；GP-UCB 加入预测标准差，能把不确定区域也纳入考虑。
4. 连续空间可以均匀填充几何区域；离散类别空间没有天然距离，所以这里只能用“覆盖水平”和“one-hot 距离”作为近似。
5. 看多个 repeat 的平均最终结果、分位区间和曲线形状；如果区间大量重叠，就不应该过度解释单次排名。
6. 先检查数据、编码、候选条件是否合理，再把建议当作可验证假设。模型不能替代化学约束和实验安全判断。
"""
        ),
        md(
            r"""
## 小结

Buchwald-Hartwig 数据让我们看到 AI4Chem 的另一个典型问题：不是预测单个分子性质，而是在有限实验预算下选择下一步实验。
random search 是必须认真比较的强 baseline；GP、RF、LHC/CVT-like 初始化都只是帮助我们更系统地提出实验假设。
surrogate model 是决策辅助工具，不是自动替代化学判断。
"""
        ),
    ]
    return notebook(cells)


NOTEBOOK_BUILDERS = {
    "00_course_map.ipynb": course_map,
    "01_molecules_as_data.ipynb": molecules_as_data,
    "02_descriptors_fingerprints_similarity.ipynb": descriptors_similarity,
    "03_esol_dataset_curation.ipynb": esol_curation,
    "04_property_prediction.ipynb": property_prediction,
    "05_model_reliability.ipynb": model_reliability,
    "06_molecular_space.ipynb": molecular_space,
    "07_reaction_optimization.ipynb": reaction_optimization,
}


EN_MARKDOWN_CELLS = {
    "00_course_map.ipynb": [
        r"""
# 00 Course Map: Learning AI + Chemistry Practice

This tutorial uses eight short modules to answer one central question: how can chemical objects become computable, modelable, and testable data tasks?

Originally prepared for the 2026 Tsinghua University AI for Chemistry Interdisciplinary Practice Summer Course, the material is now organized as a self-contained, bilingual public fast-track tutorial.

Core route:

```text
molecules/reactions -> representations -> features -> labels -> models -> evaluation -> chemical judgment
```

Application scenarios include aqueous solubility prediction, structural similarity search, applicability-domain analysis, molecular-space visualization, and reaction-condition optimization. These tasks may all look like "using AI", but the shared foundation is translating a chemical question into a traceable data problem.
""",
        r"""
## Intuition

AI4Chem is not just "putting AI on chemistry". For every task, first make the following explicit:

- Input: SMILES, descriptors, fingerprints, or reaction conditions.
- Output: solubility, yield, activity, toxicity, or another measured property.
- Data quality: units, duplicates, outliers, and experimental error.
- Evaluation: random split, scaffold split, time split, or external distribution.

Reference resources: RDKit documentation is useful for molecular representation and cheminformatics operations; scikit-learn documentation is useful for models, splits, and metrics. Delaney ESOL and the Ahneman/Doyle Buchwald-Hartwig dataset provide the main property-prediction and reaction-optimization examples.
""",
        r"""
## Mathematical and Chemical Definitions

This tutorial repeatedly uses the following notation:

```text
X: feature matrix, one row per molecule or reaction condition
y: label vector, such as logS or yield
f(X): model prediction
error = y_true - y_pred
```

A model is not a chemical law. It is an approximate function learned from finite data.
""",
        r"""
## Code

The table below breaks the full material into modules. With limited time, complete `00` to `05` first.
""",
        r"""
## Observation Questions

1. Which input type is most familiar to you: molecular structures, reaction conditions, images, spectra, or text?
2. If a model has a low test RMSE, can it necessarily guide real chemical experiments?
3. Which is easier to overlook: dataset provenance or split strategy?

### Hints

1. Start from familiar chemistry topics: organic structures are close to molecular graphs, analytical chemistry data are close to spectra/images, and experimental design is close to reaction-condition tables.
2. Not necessarily. First ask whether the test set represents the molecules, reactions, or conditions that will be predicted later.
3. Both are easy to overlook. Provenance determines whether labels are trustworthy; the split determines how strong a generalization claim the score can support.
""",
        r"""
## Summary

The goal is not to train the strongest model. The goal is to understand an AI4Chem workflow: where data come from, how molecules are encoded, how models predict, why evaluation can mislead, and how results return to chemical judgment.
""",
    ],
    "01_molecules_as_data.ipynb": [
        r"""
# 01 Molecules as Data

This section starts from SMILES. SMILES means **Simplified Molecular Input Line Entry System**. It is a way to write a molecular graph as a one-line string. SMILES is convenient for storage, search, tables, descriptors, fingerprints, and machine-learning input.

Application scenarios include chemical database search, structure deduplication, virtual screening, property prediction, and reaction SMILES representation. The classic origin is Weininger's SMILES notation; in practice, parsing behavior follows toolkits such as RDKit and Daylight.
""",
        r"""
## Intuition

SMILES can be understood as "walking through a molecular graph and writing down atoms, bonds, branches, and ring closures along the path". The same molecular graph can be traversed from different atoms, in different directions, and with different branch orders. Therefore, a single molecule often has multiple valid SMILES strings.

Example: ethanol can be written as `CCO` or `OCC`. Both represent the same molecular graph.

For deduplication and comparison, input SMILES are often converted to canonical SMILES. The software first parses the molecular graph, then uses fixed ranking and traversal rules to choose a standard string. If the molecular graph, isotopes, charges, aromaticity, stereochemistry, and related information are interpreted by the same toolkit under the same rules, the output should be deterministic.
""",
        r"""
## Mathematical and Chemical Definitions

A molecular graph can be written as:

```text
G = (V, E)
V: atoms
E: bonds
```

SMILES is one linearization of this graph, not the only one. canonical SMILES is an algorithmically selected standard linearization.

Important caveat: the "uniqueness" of canonical SMILES is practical, not absolute outside a chosen software toolkit and chemical convention. If stereochemistry, protonation state, salt form, tautomeric state, or atom mapping is not specified, two strings may still hide chemical distinctions beyond the scope of this tutorial.
""",
        r"""
## Code

RDKit can parse SMILES into molecule objects and draw 2D structures. Invalid SMILES returns `None`.
""",
        r"""
## Observation Questions

1. Do `CCO` and `OCC` have the same canonical SMILES?
2. Why can RDKit not parse `invalid_ring`?
3. What problem does canonical SMILES solve, and what does it not solve?

### Hints

1. Parse `CCO` and `OCC` separately, then compare `Chem.MolToSmiles(...)`.
2. Common invalid-SMILES causes include unclosed ring numbers, mismatched parentheses, unreasonable valence, and illegal characters.
3. canonical SMILES mainly solves deduplication and comparison when the same molecule has multiple string forms. It does not automatically solve tautomerism, protonation state, salt form, conformation, solvent, or experimental context.
""",
        r"""
## Summary

SMILES lets molecules enter tables and code; canonical SMILES makes deduplication easier. But SMILES is not all chemical information. Experimental conditions, conformations, solvents, and measurement errors still need separate records.
""",
    ],
    "02_descriptors_fingerprints_similarity.ipynb": [
        r"""
# 02 Descriptors, Fingerprints, and Similarity

This section turns molecules into numbers that models can process: descriptors and fingerprints. We first inspect a descriptor table, then introduce fingerprints, and finally compute Tanimoto similarity from fingerprints.

Application scenarios include similarity search, virtual screening, QSAR modeling, molecular clustering, and applicability-domain estimation. The Morgan/ECFP idea follows extended-connectivity fingerprints described by Rogers and Hahn; RDKit usage follows the RDKit fingerprint generator documentation.
""",
        r"""
## Intuition

A descriptor is like a molecule's resume: molecular weight, LogP, TPSA, hydrogen-bond donors, and hydrogen-bond acceptors. A fingerprint is like a checklist of structural fragments: if a local structure appears, the corresponding position is set to 1.

The two representations answer different questions:

- Descriptors are better for explaining global molecular properties, such as size, polarity, and hydrogen-bonding capacity.
- Fingerprints are better for comparing whether two molecules contain similar local structural fragments.

In this tutorial, Tanimoto similarity is usually computed from fingerprints, not directly from a small descriptor table. Mathematically, Tanimoto/Jaccard can be generalized to nonnegative vectors. For descriptors such as MolWt, LogP, and TPSA, one usually standardizes values first and then uses Euclidean distance, cosine similarity, Mahalanobis distance, or a model/kernel-based comparison. Otherwise, units and scales make the result hard to interpret.
""",
        r"""
## What Is a Fingerprint?

A fingerprint encodes molecular structure as a fixed-length vector. The most common teaching example is a binary fingerprint:

```text
bit = 1: a structural fragment appears
bit = 0: this structural fragment does not appear
```

This tutorial uses Morgan fingerprints. They start from each atom and expand the local environment layer by layer. `radius=2` roughly means considering local structures within two bonds around each atom. Common fingerprint families include:

| Fingerprint | Intuition | Common use |
| --- | --- | --- |
| Morgan/ECFP | Circular local environments around atoms | Similarity search, QSAR, virtual screening |
| MACCS keys | Predefined structural questions, such as functional-group presence | Fast teaching, interpretable filtering |
| RDKit topological fingerprint | Fragments enumerated along graph paths | General similarity search |
| Atom-pair fingerprint | Atom-pair types and topological distances | Longer-range structural relationships |
| Pharmacophore fingerprint | Pharmacophore features and spatial/topological relations | Drug-discovery similarity |

Different fingerprints change what "similar" means. Similarity is therefore not an absolute molecular property; it is the result of "representation + similarity formula".
""",
        r"""
## Mathematical and Chemical Definitions

Tanimoto similarity measures fingerprint overlap:

```text
T(A, B) = c / (a + b - c)
```

`a` is the number of active bits in A, `b` is the number of active bits in B, and `c` is the number of bits active in both A and B.

If fingerprints are treated as sets:

```text
A = set of structural fragments in molecule A
B = set of structural fragments in molecule B

T(A, B) = |A intersection B| / |A union B|
```

This is the set version of Jaccard similarity; in cheminformatics it is often called Tanimoto similarity. The intuition is: the more similar two molecules are, the larger the fraction of shared fragments among all fragments observed in either molecule.

Comparison with other similarity or distance choices:

| Method | Form / intuition | Good for | Limitation |
| --- | --- | --- | --- |
| Tanimoto/Jaccard | Shared fragments / total fragments | Sparse binary fingerprints | Does not know which fragments are more important; depends on fingerprint choice |
| Dice similarity | `2c / (a + b)`, emphasizes overlap | Binary set comparison | Often numerically higher than Tanimoto; not directly interchangeable across papers |
| Cosine similarity | Angle between vectors | Continuous vectors, embeddings, count vectors | Usable for binary fingerprints, but less common as the default chemical retrieval metric |
| Euclidean distance | Geometric distance | Standardized descriptor tables | Sensitive to scale; weak intuition on sparse high-dimensional bits |

Strengths: Tanimoto is simple, fast, bounded between 0 and 1, and well suited to sparse fingerprints.
Limitations: it only sees bit overlap. It does not know which fragment is mechanistically important, and it does not directly encode conformation, reaction conditions, experimental error, or mechanism.
""",
        r"""
## Code

The next cells compute Morgan fingerprints and pairwise Tanimoto similarity. Similarity closer to 1 means more fingerprint overlap.

Read the code in three steps:

1. Define the fingerprint rule with `GetMorganGenerator(radius=2, fpSize=1024)`.
2. Convert each SMILES into a fingerprint.
3. Use RDKit `FingerprintSimilarity` to compute pairwise Tanimoto similarity.
""",
        r"""
## Observation Questions

1. Does the similarity between benzene and toluene match your intuition?
2. Which descriptor seems most connected to aqueous solubility?
3. Fingerprint bits are not very intuitive one by one. Why are they still useful?

### Hints

1. Benzene and toluene share an aromatic ring, so Tanimoto should be relatively high. The methyl substituent adds extra fragments, so it should not be 1.
2. Start with `MolLogP`, `TPSA`, `HBD`, and `HBA`. Solubility often relates to polarity, hydrogen-bonding capacity, and hydrophobicity, but no single descriptor fully determines it.
3. Individual bits are hard to interpret, but the full bit vector efficiently represents many local structural fragments, making it useful for similarity search and machine-learning input.
""",
        r"""
## Summary

Descriptors are easier to interpret; fingerprints are better at capturing local structure. Tanimoto similarity is a fingerprint-based similarity metric, not the complete meaning of chemical similarity.
""",
    ],
    "03_esol_dataset_curation.ipynb": [
        r"""
# 03 ESOL Dataset Curation: Labels, Duplicates, and Scaffolds

This section treats ESOL as a real dataset to inspect, not as a CSV to send directly into a model. The key questions are: what does the `logS` label mean, where does the data come from, how can derived features remain traceable, and what model claim can each split support?
""",
        r"""
## Intuition

The first step in AI4Chem is not modeling, but data. Ask:

- What are the label units?
- Which paper or database is the data from?
- Can the SMILES be parsed?
- Are there duplicate or near-duplicate structures?
- Is the test set too similar to the training set?

ESOL is a classic small aqueous-solubility dataset often used for teaching molecular property prediction. It is useful for practicing descriptors, fingerprints, baselines, random split, and scaffold split. It is not a modern deployment-grade solubility benchmark.
""",
        r"""
## Mathematical and Chemical Definitions

The ESOL label is `log solubility (mol/L)`, written here as `logS`:

```text
S: aqueous solubility in mol/L
logS = log10(S / (1 mol/L))
```

For example, `logS = -3` means a solubility of about `10^-3 mol/L`. Many organic small molecules have solubility below 1 mol/L, so logS is often negative.

The ESOL data used here comes from Delaney's aqueous-solubility dataset:

> Delaney, J. S. ESOL: estimating aqueous solubility directly from molecular structure.
> Journal of Chemical Information and Computer Sciences, 2004. DOI: 10.1021/ci034243x

A scaffold is an approximation of the molecular core. A scaffold split tries to put different core structures into train and test sets, giving a stricter estimate of extrapolation to new cores.
""",
        r"""
## Split Hierarchy: Splits Define the Claim

A data split is not a minor technical detail. It defines what the model is being tested on:

| split | How it works | Claim it supports | What it cannot show |
| --- | --- | --- | --- |
| random split | Randomly sample a test set | Interpolation on similar molecules from the same distribution | Generalization to new scaffolds |
| scaffold split | Group by Murcko scaffold and keep test scaffolds mostly unseen in training | Initial extrapolation to new core structures | Still may have nearest-neighbor leakage; not source/time extrapolation |
| cluster split | Cluster by fingerprint similarity, then split by cluster | More direct control of structural similarity | Threshold choice affects the conclusion |
| source split | Split by experiment source, lab, paper, or assay | Robustness across protocols or sources | ESOL CSV lacks enough source metadata |
| time split | Split by publication year or database-entry time | Closer to future deployment | Needs reliable timestamps; not available here |
| external test | Test on a fully independent dataset | Closest to real generalization check | Expensive; label definitions must match |

In short, random split supports "interpolation among similar data". Claims about new scaffolds, new sources, or future data require stronger splits or external tests. This section inspects ESOL structure and scaffold distribution; `04` builds random-split models, and `05` compares random split with scaffold split.
""",
        r"""
## Prepare Paths

This cell only finds the `materials/` root and `data/` paths. The same paths work whether the notebook is opened from `materials/` or from `notebooks/`.
""",
        r"""
## Prepare RDKit Helper Functions

This cell defines reusable functions for parsing SMILES, generating canonical SMILES, computing descriptors, extracting Murcko scaffolds, and converting raw ESOL rows into a derived modeling table.
""",
        r"""
## Read Raw ESOL

First inspect the raw CSV: row count, column names, and a few examples. No overwriting happens here, so raw data provenance remains intact.
""",
        r"""
## Create a Traceable Derived Table

The next cell creates a derived table: it keeps the raw row id and adds canonical SMILES, descriptors, and scaffold. It does not overwrite the raw CSV.
""",
        r"""
## Check Duplicate Structures

The same molecule can have multiple SMILES forms. Grouping by canonical SMILES can reveal identity-leakage risk: if the same structure appears in both train and test, test scores may be inflated.
""",
        r"""
## Inspect Label Distribution and a Simple Trend

These plots answer two basic questions: what is the approximate range of `logS`, and is there a rough relationship between molecular weight and solubility? This is not a modeling conclusion; it is a way to understand labels and obvious outliers.
""",
        r"""
## Inspect Scaffold Distribution

Scaffold distribution affects later splits. If a scaffold is very frequent, random split will likely place similar cores in both train and test. Scaffold split is closer to the question "can the model handle new core structures?"
""",
        r"""
## Observation Questions

1. What range does ESOL logS roughly cover?
2. Is there an obvious trend between molecular weight and solubility? What are the exceptions?
3. Why should a data card record provenance, units, and limitations?

### Hints

1. Check the histogram range. Most molecules have negative logS, meaning molar solubility below 1 mol/L.
2. Higher molecular weight often means lower solubility, but this is only a weak trend. Molecules with many hydrogen-bond donors/acceptors, strongly polar groups, or ionizable states may deviate.
3. Provenance, units, and limitations determine whether labels are comparable. Without a data card, it is hard to tell whether a model learned solubility chemistry, source bias, or accidental data-processing patterns.
""",
        r"""
## Summary

Dataset curation is not merely "cleaning dirty data". It builds a traceable evidence chain. Keep raw data, make derived features reproducible, and remember that duplicates and scaffolds affect later model evaluation.
""",
    ],
    "04_property_prediction.ipynb": [
        r"""
# 04 Molecular Property Prediction: From Baselines to Random Forests

This section uses ESOL as a regression task: input molecular features, predict logS.

Application scenario: in synthesis, drug discovery, or materials screening, existing data can be used to estimate candidate properties before deciding which molecules deserve further experiments. This section compares lightweight scikit-learn models: `DummyRegressor`, `Ridge`, and `RandomForestRegressor`. The data still comes from Delaney ESOL.
""",
        r"""
## Intuition

Before modeling, build a baseline. A baseline asks: "If the model learns no structure and only predicts the training-set mean, how well does it do?" Every complex model should be compared with a baseline.

Chemically, the baseline is the reference that uses no structural information. Ridge tries to explain logS as a linear combination of descriptors. RandomForest can capture nonlinear relationships, but can also memorize local patterns in small datasets.
""",
        r"""
## Mathematical and Chemical Definitions

RMSE:

```text
RMSE = sqrt(mean((y_true - y_pred)^2))
```

MAE:

```text
MAE = mean(abs(y_true - y_pred))
```

Parity plot: true values on the x-axis and predicted values on the y-axis. Points closer to the diagonal are more accurate.
""",
        r"""
## Prepare Data and Model Tools

This part reads derived ESOL features, turns descriptors into `X`, turns logS into `y`, and creates a random train/test split. Note: random split measures interpolation within this data distribution. It does not prove extrapolation to new scaffolds.
""",
        r"""
## Code

Compare three models: mean baseline, linear Ridge, and RandomForestRegressor.
""",
        r"""
## Read the Parity Plot

This cell selects the model with the lowest test RMSE and plots true logS against predicted logS. The diagonal is not a fitted line; it is the perfect-prediction line. Larger distance from the diagonal means larger error.
""",
        r"""
## Find the Most Difficult Molecules

Average model scores only describe overall error. Also inspect failure cases: are they larger, more hydrophobic, unusual in functional groups, or located in rare regions of the training data?
""",
        r"""
## Observation Questions

1. Is RandomForestRegressor always better than Ridge?
2. What might it mean if train RMSE and test RMSE differ a lot?
3. What common structures or descriptor features appear in the worst predictions?

### Hints

1. Not always. RandomForest can model nonlinearity, but it is not guaranteed to win on small data, weak features, or out-of-distribution tests.
2. Very low train error and much higher test error often suggest overfitting, or a distribution difference between train and test.
3. Check MolWt, MolLogP, TPSA, HBD/HBA, and whether the molecule has large rings, many heteroatoms, strongly hydrophobic fragments, or structures rare in the training set.
""",
        r"""
## Summary

Property prediction should start from a baseline and then compare models. RMSE and parity plots are entry points for reading regression results, but they do not answer whether a model extrapolates to new scaffolds.
""",
    ],
    "05_model_reliability.ipynb": [
        r"""
# 05 Model Reliability: Splits, Leakage, and Applicability Domain

This section asks a more scientific question: when is a model trustworthy?

Application scenario: when a model ranks new molecules, screens candidates, or suggests experiments, a single random-split score is not enough. We need to know whether test molecules are merely nearest neighbors of training molecules, or whether they represent genuinely new chemical space.
""",
        r"""
## Intuition

If the test set contains many nearest neighbors of the training set, the model can look very good. A scaffold split is more like testing new exam questions, while a random split is more like changing numbers within the same question type.

This section uses Murcko scaffolds as an approximation of molecular core structures. The molecular-framework idea introduced by Bemis and Murcko is often used to group molecules by core scaffold. In machine-learning evaluation, scaffold split is a stricter structural-extrapolation check than random split.
""",
        r"""
## Mathematical and Chemical Definitions

Data leakage means that test information enters the training procedure. Applicability domain means the input region where model predictions have enough supporting evidence.

One simple applicability-domain proxy:

```text
nearest_train_similarity(test molecule) = max Tanimoto(test, each train molecule)
```

Lower similarity suggests that the model may be predicting out of distribution.
""",
        r"""
## Prepare Random Split and Scaffold Split

This cell builds the same ESOL feature table and then creates two splits:

- random split: randomly samples the test set and usually tests interpolation.
- scaffold split: groups by scaffold, so test-set core structures are more likely to be unseen in training.
""",
        r"""
## Code

Use the same model to compare random split and scaffold split. The larger the difference, the more the evaluation depends on split strategy.
""",
        r"""
## Estimate Applicability Domain with Nearest Training Neighbors

For each test molecule, compute its Morgan fingerprint Tanimoto similarity to every training molecule and keep the maximum value as `nearest_train_similarity`. This is not rigorous uncertainty, but it gives an intuitive applicability-domain proxy.
""",
        r"""
## Find Low-Similarity, High-Error Examples

This cell puts scaffold-split prediction error and nearest-neighbor similarity into one table. Ask whether these molecules are intrinsically difficult, or whether the training set lacks similar chemical environments.
""",
        r"""
## Visualize the Risk Relationship

Lower x-axis values mean the test molecule is farther from training molecules; higher y-axis values mean larger prediction error. If low-similarity regions show larger errors, model outputs should be treated as hypotheses, not certain conclusions.
""",
        r"""
## Observation Questions

1. Which test RMSE is higher: random split or scaffold split?
2. Are scaffold-split test molecules less similar to their nearest training neighbors?
3. How would you use a model prediction for a molecule with very low nearest similarity?

### Hints

1. Scaffold split is often higher, but the exact result depends on seed and data distribution. The key is explaining why.
2. If scaffold split successfully creates structural extrapolation, the nearest-neighbor similarity distribution should shift lower.
3. Low-similarity predictions are better treated as hypotheses requiring verification. You can request experiments, search for external similar data, or let the model abstain.
""",
        r"""
## Summary

Model reliability is not a single score. Examine splits, duplicates, nearest-neighbor similarity, failure cases, and chemical explanations together. For low-similarity samples, predictions should be treated as hypotheses rather than conclusions.
""",
    ],
    "06_molecular_space.ipynb": [
        r"""
# 06 Molecular-Space Visualization: From High-Dimensional Fingerprints to a 2D Map

This section projects fingerprints from high-dimensional space into two dimensions to help inspect molecular space.

Application scenarios include checking data coverage, finding outliers, observing property gradients, and building intuition for active learning or experimental design. This section uses scikit-learn PCA as a basic linear dimensionality-reduction method. It is useful for teaching, but it does not replace rigorous similarity or extrapolation evaluation.
""",
        r"""
## Intuition

Each molecule can be viewed as a point in fingerprint space. Similar molecules are often closer, but a 2D map is only a projection and loses information.

Chemically, the map helps ask: do hydrophobic molecules cluster? Do high-molecular-weight molecules occupy a region? Does logS vary smoothly? If no clear region appears, it does not mean the model is useless; the 2D projection may simply be insufficient for high-dimensional structure.
""",
        r"""
## Mathematical and Chemical Definitions

PCA finds directions of maximum variance and projects a high-dimensional matrix `X` onto a few principal components:

```text
X_high_dim -> PC1, PC2
```

PCA does not know chemistry. It only uses numerical variance.
""",
        r"""
## Prepare PCA Input

This cell samples ESOL molecules, computes Morgan fingerprints, and compresses them to two dimensions with PCA. `explained_variance_ratio_` reports how much numerical variance PC1/PC2 retain; it is usually not very high because fingerprints are high-dimensional and sparse.
""",
        r"""
## Code

The next plot uses color to show logS. Inspect whether spatial position relates to solubility, molecular weight, or LogP.
""",
        r"""
## Recolor Points with a Descriptor

The same 2D coordinates can be colored by different chemical quantities.

Separate two concepts: "position is determined by the fingerprint", while "color is an overlaid property used for interpretation".
""",
        r"""
## Inspect Molecules at the Projection Edges

This cell extracts molecules at extreme PC1/PC2 positions. Edge points often help explain what structural differences a PCA direction may reflect, but do not interpret PC1/PC2 as a single chemical property.
""",
        r"""
## Observation Questions

1. Are neighboring molecules on the PCA plot necessarily chemically similar?
2. Does logS color form a clear region?
3. What information is lost when a high-dimensional fingerprint is projected to two dimensions?

### Hints

1. Not necessarily. 2D proximity only means closeness along PC1/PC2; high-dimensional fingerprint differences may be compressed away.
2. A color gradient suggests that some structural differences relate to logS. Mixed colors may mean logS depends on many factors or the projection is insufficient.
3. Local structure bits, rare fragments, nonlinear relationships, and high-dimensional neighbor relations can be lost. A 2D plot is good for asking questions, not for final evidence.
""",
        r"""
## Summary

Molecular-space maps are useful for intuition, outlier detection, and storytelling, but they do not replace rigorous evaluation. 2D distance is only one compressed view of high-dimensional structure.
""",
    ],
    "07_reaction_optimization.ipynb": [
        r"""
# 07 Reaction Optimization: Buchwald-Hartwig Condition Search

This section uses real Buchwald-Hartwig data to show why reaction optimization is a sequential decision problem under limited budget.

Application scenario: when real experiments are expensive, chemists want to find high-yielding conditions within a limited number of experiments. The data comes from the Science 2018 work by Ahneman, Estrada, Lin, Dreher, and Doyle on predicting C-N cross-coupling reaction performance.

Reference:

- Ahneman, D. T.; Estrada, J. G.; Lin, S.; Dreher, S. D.; Doyle, A. G. Predicting reaction performance in C-N cross-coupling using machine learning. Science, 2018, 360, 186-190.
""",
        r"""
## Intuition

Reaction yield depends on substrate, ligand, base, additive, aryl halide, and related conditions. Because real experimental budgets are limited, we can train a surrogate model from observed experiments and ask it to suggest the next batch of conditions likely to give high yield.

Chemically, the ligand affects the metal center's electronic and steric environment; base and additive affect pathways and side reactions; aryl halide changes substrate reactivity. A model can learn associations from an existing table, but it cannot guarantee that a suggested condition is mechanistically reasonable.
""",
        r"""
## Mathematical and Chemical Definitions

A simple optimization loop:

```text
1. Observe a small set of experiments D = {(condition_i, yield_i)}
2. Train a surrogate: condition -> yield
3. Use an acquisition rule to select the next untested conditions
4. Read or run those experiments, update D
```

This section compares three strategy families:

1. random search: no learning; randomly sample conditions.
2. Random Forest greedy: train an RF surrogate on one-hot conditions and select the highest predicted mean.
3. Gaussian Process UCB: use a GP surrogate and select by `mean + beta * std`, balancing prediction and uncertainty.

To mimic high-throughput experimentation, this section uses batch optimization: each round selects 5 candidate conditions, waits until the whole batch is observed, then trains the next model.

Three initial designs are included:

- random initial design: randomly choose the first 5 conditions.
- Latin-like level coverage: cover different levels of each discrete factor as much as possible, similar to the LHC idea of covering dimensions.
- CVT-like/maximin: greedily choose points that are far apart in one-hot space, similar to space-filling or CVT-style coverage.

Strict LHC and CVT are mainly defined for continuous spaces. Reaction conditions here are discrete categorical variables, so these are categorical approximations.

The plot therefore contains 7 main curves: 1 random baseline plus `3 initial designs x 2 surrogate models`. Each curve uses 10 repeats and shows a mean with a 10-90% band, avoiding overinterpretation of one random seed.
""",
        r"""
## Read Buchwald-Hartwig Data

This cell reads the reaction-condition table and converts yield to numeric values. Each row is a measured condition combination. The simulation "reads" results from a fixed table; it does not run new wet-lab experiments.
""",
        r"""
## Define the Full Candidate Space

`reaction` represents substrate/reaction identity; ligand, additive, base, and aryl halide represent selectable reaction conditions. If a condition combination has repeated records, the mean yield is used so duplicates do not distort the optimization trace.
""",
        r"""
## Inspect Yield Distribution

If high-yielding conditions are rare, random search needs a larger budget to find them. If high-yielding conditions are common, random search can perform surprisingly well.
""",
        r"""
## How Rare Are High-Yielding Conditions?

If high-yielding conditions are not rare, random search is a strong baseline. This is why optimization studies must report random baselines carefully. The next cell checks the fraction of candidates above several yield thresholds.
""",
        r"""
## Encode Reaction Conditions

scikit-learn models cannot directly process string categories. One-hot encoding turns each categorical level into a 0/1 feature: whether a row uses a particular ligand, base, reaction id, and so on.

This is a simple representation. It can express whether a condition appears, but it does not explicitly encode coordination chemistry, electronic effects, or substrate similarity.
""",
        r"""
## Define Random Search and Initial Designs

In reaction optimization, the first experiments are often designed to cover different ligands, bases, additives, or substrate types. The functions below define a batch random baseline and random/Latin-like/CVT-like initial designs.
""",
        r"""
## Define Surrogate Optimization Loops

RF greedy only uses predicted mean and can exploit too early. GP-UCB uses both predicted mean and uncertainty:

```text
acquisition(x) = mean(x) + beta * std(x)
```

Larger `beta` encourages exploration of uncertain regions.

Each round selects a whole batch of candidates. The 5 points in one batch are selected simultaneously; the result of point 1 cannot update the choice of points 2-5 within the same batch.
""",
        r"""
## Compare Search Strategies

Each curve shows the best yield observed after each batch round. The black dashed line is the global best yield in this fixed table; in real experiments this line is usually unknown.

The random baseline means "select 5 unobserved candidates randomly each round, and remain random in the next round". It does not train a model, but it avoids repeated candidates. Surrogate methods use random/Latin-like/CVT-like design for the first 5 points, then use RF or GP-UCB to choose later batches.

To reduce randomness, each strategy runs 10 repeats. The x-axis is round: round 1 means the first batch of 5 experiments has completed, and round 20 corresponds to 100 total experiments.

If random search and surrogate search are close, possible reasons include:

1. The candidate space is not large relative to the budget.
2. High-yielding candidates are not rare.
3. One-hot categorical features are crude and do not encode reaction mechanism.
4. Early surrogate models are unstable with little observed data.
""",
        r"""
## Numerical Summary

The next table compares the final best observed values for random search and the 6 surrogate combinations across 10 repeats. The point is not to prove one method always wins, but to learn how to read mean performance and uncertainty bands.

If `RF + random init` is best in one run, that does not automatically mean it is stably better than GP or space-filling initialization. RF can be strong on one-hot categorical tables; GP-UCB uncertainty can also be poorly calibrated in sparse high-dimensional one-hot space. Use repeated means and 10-90% intervals before making a claim.
""",
        r"""
## Inspect Good Conditions Observed by Surrogates

Finally, list the top-yielding conditions observed in the best repeat of each surrogate combination. The analysis focus is not only whether a model won, but whether the suggested conditions are chemically plausible and whether further diversity should be explored when experiments are expensive.
""",
        r"""
## Observation Questions

1. Why can a surrogate loop look similar to random search when only one reaction id is fixed?
2. With batch size = 5, why can the first point in a batch not update the other four points?
3. What is the essential difference between RF greedy and GP-UCB acquisition?
4. Why are LHC/CVT-style space-filling designs more natural for continuous variables? How should they be interpreted for discrete reaction conditions?
5. If `RF + random init` is best in a single run, how can you decide whether that is chance or a stable advantage?
6. If a model-suggested condition conflicts with chemical intuition, should you trust the model or recheck data and assumptions?

### Hints

1. With a fixed reaction id, the space is small. If high-yielding conditions are not rare, random search can find good conditions quickly. Early RF models also have little data, and one-hot features are crude.
2. Batch experiments are submitted in parallel. The yields are known only after the whole batch finishes, so the model cannot update sequentially within the batch.
3. RF greedy uses only predicted mean and leans toward exploitation. GP-UCB adds predicted standard deviation, so uncertain regions can also be selected.
4. Continuous spaces have natural geometry for uniform coverage. Discrete categorical spaces lack a natural distance, so this tutorial approximates coverage by factor levels and one-hot distance.
5. Check the mean final result, percentile band, and curve shape across repeats. If intervals overlap heavily, do not overinterpret a single ranking.
6. First check data, encoding, and candidate feasibility. Treat the recommendation as a testable hypothesis; models do not replace chemical constraints or experimental safety.
""",
        r"""
## Summary

Buchwald-Hartwig data shows another common AI4Chem problem: not predicting one molecular property, but choosing next experiments under a limited budget. Random search is a strong baseline that must be taken seriously. GP, RF, and LHC/CVT-like initialization are tools for proposing experimental hypotheses more systematically. A surrogate model supports decisions; it does not replace chemical judgment.
""",
    ],
}


CODE_REPLACEMENTS = {
    "# 这一格只做 inventory：确认本课程自带哪些数据文件，以及每个文件服务哪个教学任务。": "# This inventory cell checks which data files are included and which teaching task each file supports.",
    '"课程地图"': '"Course map"',
    '"知道任务框架和学习路线"': '"Understand the task framework and learning path"',
    '"分子如何变成数据"': '"Molecules as data"',
    '"会读 SMILES、canonical SMILES、分子图"': '"Read SMILES, canonical SMILES, and molecular graphs"',
    '"描述符与 fingerprint"': '"Descriptors and fingerprints"',
    '"理解 descriptor、Morgan fingerprint、Tanimoto"': '"Understand descriptors, Morgan fingerprints, and Tanimoto"',
    '"ESOL 数据整理"': '"ESOL dataset curation"',
    '"知道标签、重复、scaffold 和 provenance"': '"Understand labels, duplicates, scaffolds, and provenance"',
    '"性质预测"': '"Property prediction"',
    '"训练 baseline、Ridge、RandomForestRegressor"': '"Train baseline, Ridge, and RandomForestRegressor models"',
    '"模型可靠性"': '"Model reliability"',
    '"比较 random split 和 scaffold split"': '"Compare random split and scaffold split"',
    '"分子空间"': '"Molecular space"',
    '"用 PCA 看高维 fingerprint 的二维投影"': '"Use PCA to inspect a 2D projection of high-dimensional fingerprints"',
    '"反应优化"': '"Reaction optimization"',
    '"用 Buchwald-Hartwig 数据理解 surrogate 搜索"': '"Use Buchwald-Hartwig data to understand surrogate search"',
    '"编号"': '"No."',
    '"主题"': '"Topic"',
    '"学习目标"': '"Learning goal"',
    "# 这一格先读取示例分子表。后面每个分子都会被 RDKit 解析成 molecule object。": "# This cell reads the example molecule table. Later each molecule is parsed by RDKit into a molecule object.",
    "# MolFromSmiles 会把字符串解析成 RDKit 分子图；解析失败时返回 None。": "# MolFromSmiles parses a string into an RDKit molecular graph; failed parsing returns None.",
    "# SVG 是矢量图，放大后仍然清晰；subImgSize 越大，legend 中的 SMILES 越容易读。": "# SVG is a vector format and remains clear when zoomed; larger subImgSize makes legend SMILES easier to read.",
    "# 这一格把每个示例分子的 SMILES 转成一组容易解释的 descriptor。": "# This cell converts each example SMILES into interpretable descriptors.",
    "# 先看 descriptor 表，是为了把“分子变成数字”这件事落到可读的化学量上。": "# Inspect descriptors first so that \"molecules become numbers\" is grounded in readable chemical quantities.",
    "# radius 控制看多大的局部环境，fpSize 控制压缩到多少个 bit。": "# radius controls the local environment size; fpSize controls the number of compressed bits.",
    "# sim[i, j] 是第 i 个分子和第 j 个分子的 Tanimoto similarity。": "# sim[i, j] is the Tanimoto similarity between molecule i and molecule j.",
    "# 热图把相似性矩阵画出来；对角线一定是 1，因为每个分子和自己完全相同。": "# The heatmap shows the similarity matrix; the diagonal is 1 because each molecule is identical to itself.",
    "# 改 pair 可以快速检查“数值相似性”和你的化学直觉是否一致。": "# Change pair to quickly compare numerical similarity with chemical intuition.",
    "# raw 只包含 SMILES 和实验标签；派生列会在后面新建，不直接写回 raw CSV。": "# The raw table only contains SMILES and experimental labels; derived columns are created later and not written back to the raw CSV.",
    "# build_esol_features 会跳过 RDKit 不能解析的 SMILES，并保留原始 row_id。": "# build_esol_features skips SMILES that RDKit cannot parse and keeps the original row_id.",
    "# canonical_smiles 相同，说明 RDKit 认为它们是同一个标准化后的分子图。": "# Identical canonical_smiles means RDKit treats them as the same standardized molecular graph.",
    "# 左图看标签分布，右图看一个简单 descriptor 与标签的关系。": "# The left plot shows the label distribution; the right plot checks one simple descriptor-label relationship.",
    "# 空 scaffold 常见于无环分子；这里把它显示成更容易读的标签。": "# Empty scaffolds often occur for acyclic molecules; here they are displayed with a readable label.",
    "# X 是分子 descriptor 矩阵；y 是实验 logS 标签。": "# X is the molecular descriptor matrix; y is the experimental logS label.",
    "# 这里先用 random split 训练入门模型；更严格的 scaffold split 放到下一章。": "# This introductory model uses random split first; the stricter scaffold split appears in the next section.",
    "# clone 确保每个模型都是未训练的新实例，避免上一个模型状态泄漏。": "# clone ensures each model starts as a fresh unfitted instance, avoiding state leakage from a previous model.",
    "# abs_error 帮我们找到这次 test split 中预测偏差最大的分子。": "# abs_error helps find the molecules with the largest prediction deviations in this test split.",
    "# random split 不关心化学骨架，只随机抽样。": "# random split ignores chemical scaffolds and samples randomly.",
    "# GroupShuffleSplit 保证同一个 scaffold group 不会同时进入 train/test。": "# GroupShuffleSplit keeps the same scaffold group from entering both train and test.",
    "# 固定模型，只改变 split；这样差异主要来自评价设置，而不是模型选择。": "# Keep the model fixed and change only the split, so differences mainly come from evaluation setup rather than model choice.",
    "# BulkTanimotoSimilarity 一次计算当前测试分子和所有训练分子的相似度。": "# BulkTanimotoSimilarity computes similarities between the current test molecule and all training molecules at once.",
    "# 为了运行快，只抽取最多 600 个分子；random_state 保证每次结果可复现。": "# For speed, sample at most 600 molecules; random_state makes the result reproducible.",
    "# PCA 只看 fingerprint 矩阵的数值方差，不知道 logS 或化学机制。": "# PCA only sees numerical variance in the fingerprint matrix; it does not know logS or chemical mechanisms.",
    "# 如果颜色形成连续区域，说明二维投影捕捉到一部分和 logS 相关的结构差异。": "# If colors form continuous regions, the 2D projection captures some structure differences related to logS.",
    "# 取 PC1/PC2 两端的分子，看看二维图边缘到底是什么结构。": "# Select molecules at both ends of PC1/PC2 to inspect what structures appear near the plot edges.",
    "# 原始表中每行是一组 reaction + ligand/base/additive/aryl halide 条件和对应 yield。": "# Each raw-table row is a reaction plus ligand/base/additive/aryl halide condition and the corresponding yield.",
    "# 一个候选点就是 reaction + 条件组合；重复测量时用平均产率表示该候选点。": "# One candidate is a reaction plus condition combination; repeated measurements are represented by the mean yield.",
    "# 统计每类条件有多少种选择，用于量化组合空间为什么很快变大。": "# Count levels in each condition category to quantify why the combinatorial space grows quickly.",
    "# 在每个 batch 完成后记录“目前见过的最好产率”。": "# After each batch, record the best yield observed so far.",
    "# 如果最后一个 batch 不满 batch_size，也记录最终结果。": "# If the final batch is smaller than batch_size, still record the final result.",
    "# Baseline: 每一轮随机选 batch_size 个未观察候选；下一轮仍然随机，不训练模型。": "# Baseline: each round randomly selects batch_size unobserved candidates; the next round is still random and no model is trained.",
    "# 这个过程只利用 observed set 来避免重复选择，不利用 observed yield 来指导下一轮。": "# This process only uses the observed set to avoid repeats; it does not use observed yields to guide the next round.",
    "# 初始 batch 的随机设计。": "# Random design for the initial batch.",
    "# 离散版“Latin-like”初始化：每一步优先选择能覆盖更多未见类别水平的候选。": "# Discrete Latin-like initialization: each step prefers candidates that cover more unseen categorical levels.",
    "# gain 相同的时候随机打破平局，避免总是受原始表顺序影响。": "# Break ties randomly when gain is equal, avoiding dependence on raw-table order.",
    "# CVT-like / space-filling 思路：在 one-hot 空间中贪心选择离已有点最远的候选。": "# CVT-like / space-filling idea: greedily select candidates farthest from existing points in one-hot space.",
    "# 去重并保证初始化数量不超过 batch size、预算和候选数量。": "# Deduplicate and ensure the initialization size does not exceed batch size, budget, or candidate count.",
    "# 从 remaining 中取 acquisition score 最高的 k 个候选，作为下一批实验。": "# Select the k remaining candidates with the highest acquisition scores as the next experimental batch.",
    "# Greedy acquisition: 每轮一次性选择预测均值最高的一批候选。": "# Greedy acquisition: each round selects a whole batch with the highest predicted means.",
    "# DotProduct kernel 在 one-hot 类别特征上相当于学习线性相似性；": "# DotProduct kernel on one-hot categorical features is similar to learning linear similarity;",
    "# WhiteKernel 表示观测噪声。这里关闭超参数优化，使运行更快、更稳定。": "# WhiteKernel represents observation noise. Hyperparameter optimization is disabled for speed and stability.",
}


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def translate_code_source(source: str, filename: str) -> str:
    text = source
    for old, new in CODE_REPLACEMENTS.items():
        text = text.replace(old, new)
    if has_cjk(text):
        raise ValueError(f"English code cell in {filename} still contains CJK text")
    return text


def english_notebook(filename: str, source_notebook: dict) -> dict:
    markdown_sources = EN_MARKDOWN_CELLS[filename]
    markdown_index = 0
    cells = []

    for cell in source_notebook["cells"]:
        source = "".join(cell.get("source", []))
        if cell["cell_type"] == "markdown":
            if markdown_index >= len(markdown_sources):
                raise ValueError(f"Missing English markdown translation for {filename}")
            english_source = markdown_sources[markdown_index]
            markdown_index += 1
            cells.append(md(english_source))
        elif cell["cell_type"] == "code":
            cells.append(code(translate_code_source(source, filename)))
        else:
            raise ValueError(f"Unsupported cell type in {filename}: {cell['cell_type']}")

    if markdown_index != len(markdown_sources):
        raise ValueError(f"Unused English markdown translations for {filename}")

    return notebook(cells)


def write_notebook(path: Path, nb: dict) -> None:
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    ZH_NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    for filename, builder in NOTEBOOK_BUILDERS.items():
        zh_notebook = builder()
        write_notebook(NOTEBOOK_DIR / filename, english_notebook(filename, zh_notebook))
        write_notebook(ZH_NOTEBOOK_DIR / filename, zh_notebook)


if __name__ == "__main__":
    main()
