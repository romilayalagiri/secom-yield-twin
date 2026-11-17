# Lightweight Digital Twin for Semiconductor Yield Prediction

MSc Applied Data Science and Analytics, SRH University Hamburg.
Statistical process control (SPC) versus machine learning on the SECOM dataset,
evaluated with time-aware validation.

## Project structure

```
secom-yield-twin/
├── data/
│   ├── raw/            SECOM files as downloaded (not stored in Git)
│   └── processed/      DuckDB database created by the pipeline
├── docs/
│   ├── decision_log.md every data / method decision and why
│   └── reading_notes.md
├── notebooks/          exploration only; final code lives in src/
├── src/
│   ├── config.py       paths and expected dataset facts
│   ├── download.py     step 1: download SECOM
│   └── ingest.py       step 2: validate and load into DuckDB
├── tests/              automated checks (pytest)
├── requirements.txt    pinned library versions
├── Makefile            short commands
└── Dockerfile          reproducible environment
```

## How to run (from a fresh clone)

Requires Python 3.11.

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt

python -m src.download   # get SECOM
python -m src.ingest     # check and load into DuckDB
pytest -v                # all tests should pass
```

With `make` installed: `make setup` then `make all`.
With Docker: `docker build -t secom-twin .` then `docker run secom-twin`.

## Data

SECOM, McCann & Johnston (2008), UCI Machine Learning Repository:
https://archive.ics.uci.edu/dataset/179/secom
1,567 production runs, 590 anonymised sensors, timestamp, pass/fail label.
Licence: to be verified and recorded in `docs/decision_log.md` (Week 1).

## Use of AI tools

AI coding assistants (Claude) were used to help create the initial project
structure and code. All code is reviewed, understood and tested by the author.
See the methodology chapter of the thesis for details.
