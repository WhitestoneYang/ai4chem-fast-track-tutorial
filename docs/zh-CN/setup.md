# 环境安装与使用

建议先完整执行一次环境验证，确认 notebook、数据和依赖都能正常运行。

## 1. 安装 Miniconda 或 Anaconda

如果已经安装 conda，可以跳过。推荐使用 conda，是因为 RDKit 与科学计算依赖在不同系统上的二进制包更稳定。

## 2. 创建课程环境

在 `ai4chem-fast-track-tutorial` 目录运行：

```bash
cd ai4chem-fast-track-tutorial/
conda env create -f environment.yml
conda activate ai4chem-practice
```

如果环境已存在，更新依赖：

```bash
conda activate ai4chem-practice
pip install -r requirements.txt
```

## 3. 验证环境

```bash
python validate_ai4chem-fast-track-tutorial.py
python smoke_test.py
```

`validate_ai4chem-fast-track-tutorial.py` 不需要 RDKit，用于检查文件结构、数据列和 notebook 语法。`smoke_test.py` 会真正运行 RDKit、描述符计算、ESOL 建模和 Buchwald-Hartwig 搜索流程。

## 4. 启动 Jupyter

```bash
jupyter lab
```

打开：

```text
notebooks/00_course_map.ipynb
```

建议按编号顺序学习。时间有限时，可先完成 `00` 到 `05`，再继续 `06` 和 `07`。

## 5. 常见问题

- 找不到 `conda`：需要先安装 Miniconda/Anaconda，并重新打开终端。
- RDKit import 失败：确认已经 `conda activate ai4chem-practice`。
- notebook 找不到数据：确认当前目录是 `ai4chem-fast-track-tutorial`，并且存在 `data/raw/esol.csv`。
- 图不显示：重启 kernel 后从 notebook 第一格重新运行。

