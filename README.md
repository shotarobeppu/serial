#  serial

This repo implements the serial dictatorship algorithm for matching students and schools for university exchange programs.

## Run

### Modules

Run the following with your \<env>

``
conda create --name <env> --file requirements.txt
``

### Analysis

**iterate_max_school_applied.py** runs all the analysis with varying number of maximum schools a student can apply

The above uses modules in the ``src`` folder

### Data

data comes from university's exchange program and thus cannot be shared without consent

##  Folder structure

```
.
├── README.md
├── code
│   ├── iterate_max_school_applied.py
│   ├── test_class.py
│   ├── src
│   │   ├── algorithm.py
│   │   ├── school.py
│   │   ├── student.py
│   │   ├── utils.py
│   │   └── validate.py
├── data
│   ├── output
│   │   ├── result.xlsx (final matching result)
│   └── raw
│       ├── ...
└── output
    └── sim.png (simulation result)

```
