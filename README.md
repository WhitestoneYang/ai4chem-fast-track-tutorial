# AI4Chem 基础实践教程

[English](README.en.md) | 简体中文

一套自给自足的 Jupyter 教程，面向希望入门 AI for Chemistry 的低年级本科生。教程从分子表示开始，逐步进入 descriptor、fingerprint、相似性、数据整理、性质预测、模型可靠性、分子空间可视化和反应优化。

本教程最初为“2026年清华大学 AI for Chemistry 交叉实践暑期课程”准备，现整理为一套自给自足、双语、可公开使用的 4-8 小时 AI4Chem 快速入门教程。

本仓库可以离线运行：notebook、示例数据、数据卡和验证脚本都包含在 `materials/` 中。

## 致谢与数据来源

本教程受 Schwaller group 开源课程 [`schwallergroup/ai4chem_course`](https://github.com/schwallergroup/ai4chem_course) 的启发，是一个短时快速入门教程，目标是帮助自学者在 4-8 小时内掌握 AI4Chem 的基础。希望系统完整学习 AI4Chem 的读者，建议进一步参考 Schwaller group 的原课程。

教程使用并标注了以下公开数据和文献来源：

- ESOL 水溶性数据：Delaney, J. S. *Journal of Chemical Information and Computer Sciences*, 2004. https://doi.org/10.1021/ci034243x
- Buchwald-Hartwig C-N cross-coupling 数据：Ahneman, D. T.; Estrada, J. G.; Lin, S.; Dreher, S. D.; Doyle, A. G. *Science*, 2018. https://doi.org/10.1126/science.aar5169

数据字段、用途和限制见 `data/cards/`。软件和文献链接汇总见 `docs/zh-CN/references.md`。

## 学习路径

- 4h：`00` -> `01` -> `02` -> `03` -> `04` -> `05`
- 6h：4h 路线 + `06_molecular_space.ipynb`
- 8h：完整运行 `notebooks/zh-CN/00_course_map.ipynb` 到 `notebooks/zh-CN/07_reaction_optimization.ipynb`，并完成 `worksheet.zh-CN.md`

## Notebook 目录

| Notebook                                         | Topic                                            |
| ------------------------------------------------ | ------------------------------------------------ |
| `00_course_map.ipynb`                          | 课程地图：AI+化学实践如何学习                    |
| `01_molecules_as_data.ipynb`                   | SMILES、canonical SMILES、分子可视化             |
| `02_descriptors_fingerprints_similarity.ipynb` | descriptor、fingerprint、Tanimoto similarity     |
| `03_esol_dataset_curation.ipynb`               | ESOL 数据整理、LogS、scaffold split              |
| `04_property_prediction.ipynb`                 | baseline、Ridge、RandomForest、RMSE、parity plot |
| `05_model_reliability.ipynb`                   | split、data leakage、applicability domain        |
| `06_molecular_space.ipynb`                     | fingerprint PCA 和分子空间可视化                 |
| `07_reaction_optimization.ipynb`               | Buchwald-Hartwig 反应优化和 surrogate loop       |

## 快速开始

```bash

cd ai4chem-fast-track-tutorial/
conda env create -f environment.yml
conda activate ai4chem-practice
jupyter lab notebooks/zh-CN/00_course_map.ipynb
```

* [ ] 详细安装说明见 `docs/zh-CN/setup.md`。

## 仓库结构

```text
ai4chem-fast-track-tutorial/
├── notebooks/              # 英文 notebook
│   └── zh-CN/              # 中文 notebook
├── data/
│   ├── raw/                # ESOL 与 Buchwald-Hartwig *.CSV data
│   ├── examples/           # 小型示例分子表
│   └── cards/              # 数据卡和来源说明
├── docs/                   # 英文文档
│   └── zh-CN/              # 中文文档
├── worksheets/             # 英文讨论任务
│   └── zh-CN/              # 中文讨论任务
├── worksheet.md            # 英文学习记录表
├── worksheet.zh-CN.md      # 中文学习记录表
├── environment.yml         # Conda 环境
└── requirements.txt        # pip 依赖
```

## License

本仓库中的原创教程文本、代码和 notebook 结构以 MIT License 发布，见 `LICENSE`。