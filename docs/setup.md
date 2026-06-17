# Setup and Usage

Run the validation scripts once before working through the notebooks. This confirms that the repository structure, data files, and installed dependencies are usable.

## 1. Install Miniconda or Anaconda

If `conda` is already installed, skip this step. Conda is recommended because RDKit and scientific Python dependencies are distributed as stable binary packages across operating systems.

## 2. Create the Tutorial Environment

From the `materials` directory:

```bash
conda env create -f environment.yml
conda activate ai4chem-practice
```

If the environment already exists, update Python packages:

```bash
conda activate ai4chem-practice
pip install -r requirements.txt
```

## 3. Validate the Environment

```bash
python validate_materials.py
python smoke_test.py
```

`validate_materials.py` does not require RDKit. It checks file structure, data columns, notebook JSON, and Python syntax. `smoke_test.py` actually runs RDKit, descriptor calculation, fingerprint generation, ESOL modeling, and the Buchwald-Hartwig search workflow.

## 4. Start Jupyter

```bash
jupyter lab
```

Open:

```text
notebooks/00_course_map.ipynb
```

Work through the notebooks in order. With limited time, complete `00` to `05` first, then continue to `06` and `07`.

## 5. Common Issues

- `conda` is not found: install Miniconda/Anaconda and reopen the terminal.
- RDKit import fails: confirm that `conda activate ai4chem-practice` has been run.
- A notebook cannot find data: confirm the current working directory is `materials` and `data/raw/esol.csv` exists.
- Figures do not display: restart the kernel and rerun from the first cell.
