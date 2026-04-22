# UN-ASP: Handling Numerical Uncertainty

----------------------------------------

This repository contains a prototypal implementation of the semantics presented in the paper **"UN-ASP: Handling Numerical Uncertainty"**, together with the source code used to conduct the evaluation on a real-world dataset.

### Project structure

----------------------------------------

- **data/**
  - `nari_dynamic.csv` —  Dataset used in the evaluation containing the positional information of the vessels
  - `nari_static.csv` —  Dataset used in the evaluation containing the structural information of each vessel 
  - `vessel_processing.ipynb` — Notebook for data preprocessing and analysis

- **src/**
  - **asp_code/** — ASP programs (original and rewritten)
  - **parser/** — Utilities for parsing ASP programs and directives
  - `approximation.py` — Implementation of the approximation mapping $\mu$
  - `rewriter.py` — The original ASP program is rewritten to include calls to external predicates.

- **tests/**
  - `test_discreteclusters.py` — Unit tests for core components
  - `test_parser.py` — Unit tests for core components
  - `test_rewriter.py` — Unit tests for core components

- `README.md`


### How to run the code

----------------------------------------

1. In order to use the new semantics, the original program must be rewritten.  The user must include in the program the following directive that indicates which predicate is considered uncertain and must be approximated:\
`#uncertain p/a, t. rho=v_1, sigma=v_2.`\
Where `p` is the name of the uncertain predicate, `a` is the arity of the predicate, `t` is the position of the term considered uncertain, `v_1` and `v_2` are, respectively, the values assigned to $\rho$ and $\sigma$.\
2. Once the directive has been added to the program, it can be rewritten using the `rewriter` script available in the repository.
`python3 -m src.rewriter ./src/asp_code/file.lp`
3. After the program has been rewritten, the new rewritten program must be run using DLV2 with the option that enables paracoherent semantics. In addition, the file containing the code for applying the approximation mapping $\mu$ to the values considered uncertain (`approximation.py`) must also be provided as input.\
`dlv2 --paracoherent=semiequilibrium ./src/asp_code/rewritten_file.lp ./src/approximation.py`

### Notes

----------------------------------------

To run the vessel_processing.ipynb file, you must first download the dataset at [https://zenodo.org/records/1167595](https://zenodo.org/records/1167595?preview_file=%5BP1%5D+AIS+Data.zip) .