# One-word commands (Mac/Linux, or Windows with Git Bash + make).
# Without make, run the python commands shown after each target.

.PHONY: setup data ingest test all

setup:   ## install the pinned libraries
	pip install -r requirements.txt

data:    ## python -m src.download
	python -m src.download

ingest:  ## python -m src.ingest
	python -m src.ingest

test:    ## pytest -v
	pytest -v

all: data ingest test
