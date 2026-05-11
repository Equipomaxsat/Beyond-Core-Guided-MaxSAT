# Beyond Core-Guided MaxSAT

This repository contains the prototype MaxSAT solvers used in the paper:

> Ilario Bonacina, Jordi Levy, and Ion Mikel Liberal.  
> **Beyond Core-Guided MaxSAT**.  
> *29th International Conference on Theory and Applications of Satisfiability Testing (SAT 2026)*.  
> Leibniz International Proceedings in Informatics (LIPIcs), Article No. 8, pp. 8:1--8:18, 2026.  
> DOI: `10.4230/LIPIcs.SAT.2026.8`.

The paper introduces the **Comparator Calculus (CC)**, a proof system for MaxSAT designed to model the inferential behaviour of SAT-based and core-guided MaxSAT solvers. Inspired by this calculus, the paper studies two main families of algorithms:

- **CSimple**, a core-guided MaxSAT algorithm that replaces an unsatisfiable core by a shallow comparator construction computing the conjunction of the core.
- **CSat**, a SAT-based MaxSAT algorithm that is not purely core-guided: it keeps a set of models of the hard clauses, uses them to construct candidate soft formulas by comparator operations, and calls the SAT solver to certify whether those candidates are unsatisfiable.

The code in this repository is a research prototype. It was written to support the experimental comparison in the paper between CSimple, CSat, core-guided variants of CSat, OLL-style solving, and Fu&Malik-style baselines.

## Requirements

The code is written in Python and depends on:

- Python 3
- `optilog`, for the Glucose 4.1 SAT solver interface
- `bitarray`, used by the CSat implementation

For example:

```bash
pip install bitarray
```

Install `optilog` following the installation instructions for your system or local environment.

## Input format

The solvers read weighted partial MaxSAT instances in a WCNF-like format. In particular:

- soft clauses have a positive integer weight;
- hard clauses can be written with leading `h`;
- alternatively, a clause whose weight is at least the top weight in the problem line is treated as hard;
- every clause must end in `0`.

Example:

```text
p wcnf 3 4 10
1 1 0
2 -1 2 0
h -2 3 0
h -3 0
```

The parser is implemented in `tools.py`.

## Main programs

### `comp.py`: CSat and core-guided CSat

This file implements the CSat-style algorithms based on comparator operations between soft formulas.

Main class:

- `Comparator`: inherits from `MaxSATsolver` and implements CSat.

Important options:

- `-m`, `--initmodels`: number of initial models used to initialize the matrix of assignments.
- `-H`, `--heuristic`: heuristic used to select pairs of soft formulas. Use `1` or `2`.
- `-c`, `--coreguided`: restricts the heuristic to formulas coming from a SAT core.
- `-i`, `--incremental`: keeps the same SAT solver instance between calls instead of restarting it.
- `-s`, `--seed`: random seed.
- `-v`, `--verbose`: prints additional information.

Examples:

```bash
python3 comp.py instance.wcnf
python3 comp.py instance.wcnf -H 1
python3 comp.py instance.wcnf -H 2
python3 comp.py instance.wcnf -H 1 -c
python3 comp.py instance.wcnf -H 2 -c -m 5 -s 1
```

The non-core-guided versions correspond to CSat with heuristics 1 and 2. The option `-c` activates the core-guided versions of CSat.

### `simple.py`: CSimple

This file implements the CSimple algorithm described in the paper. After extracting a core, it builds a comparator network computing the conjunction of the core and keeps the remaining comparator outputs as soft formulas.

Main components:

- `conjunctionNetwork(C, lv)`: recursively builds the comparator construction for a core `C` starting after variable `lv`.
- `OLL`: solver class implementing the CSimple behaviour. The class name is historical; the algorithm implemented here is the CSimple-style solver used in the paper.

Examples:

```bash
python3 simple.py instance.wcnf
python3 simple.py instance.wcnf -i
python3 simple.py instance.wcnf -s 7 -v
```

Options:

- `-i`, `--incremental`: keeps learned clauses between SAT calls.
- `-s`, `--seed`: random seed.
- `-v`, `--verbose`: prints additional information.

### `FuMalik.py`: Fu&Malik baseline

This file implements a Fu&Malik-style core-guided MaxSAT solver using a sorting-network encoding of the at-most-one constraint over relaxation variables.

Main class:

- `FuMalik`: inherits from `MaxSATsolver`.

Example:

```bash
python3 FuMalik.py instance.wcnf
```

Options:

```bash
python3 FuMalik.py instance.wcnf -s 1 -v
```

The parser accepts an `-i` option for consistency, but the implementation explicitly rejects incremental mode because this algorithm is not intended to work incrementally in the current code.

### `FuMalikSymBreak.py`: Fu&Malik with symmetry breaking

This file implements a Fu&Malik-style solver with a symmetry-breaking mechanism. Instead of adding a full cardinality network over relaxation variables, it repairs the first unsatisfied formula according to the core order, following the symmetry-breaking variant discussed in the paper.

Main class:

- `FuMalik`: inherits from `MaxSATsolver`.

Example:

```bash
python3 FuMalikSymBreak.py instance.wcnf
```

As in `FuMalik.py`, incremental mode is rejected by the implementation.

## Supporting files

### `maxSATsolver.py`

Base class for all solvers.

Main class:

- `MaxSATsolver`

Main responsibilities:

- stores hard clauses, soft literals and weights;
- transforms general soft clauses into unary soft clauses using blocking variables;
- creates and restarts the underlying Glucose 4.1 solver;
- wraps SAT calls with assumptions;
- records the time spent in SAT calls;
- records the current cost, number of cores and number of comparators;
- prints final results in a uniform format.

### `tools.py`

Utility functions for manipulating formulas and reading/writing files.

Main functions:

- `maxVar(F)`: maximum variable index occurring in a formula.
- `foldWCNF(S, H)`: merges duplicate soft clauses and removes duplicate hard clauses.
- `unarySoft(S, H)`: converts soft clauses into unary soft clauses with blocking variables.
- `evaluate(F, M)`: evaluates a MaxSAT or XOR formula under a model.
- `printCNF`, `printWCNF`, `printXOR`: output utilities.
- `readWCNF`, `readXOR`: input parsers.

### `cardinality.py`

Encodings and helper routines for cardinality-style constructions.

Main functions:

- `comparator(i1, i2, o1, o2)`: CNF encoding of a comparator with inputs `i1`, `i2` and outputs `o1`, `o2`.
- `sortingNetwork(input, lastvar)`: builds a sorting network over the input literals.
- `bubbleSort(input, lastvar)`: alternative comparator-based sorting construction.
- `totalizer(input, lastvar)`: totalizer encoding for cardinality constraints.

### `generators.py`

Small benchmark generator.

Supported models:

- `rnd`: random CNF formula, written as WCNF with unit weights.
- `php`: pigeonhole principle instance, with at-least-one pigeon clauses soft and at-most-one pigeon clauses hard.
- `xor`: random XOR formula.
- `cut`: random cut-style XOR formula.
- `sw`: small-world-style random formula.

Examples:

```bash
python3 generators.py php -n 5 -m 25 -o php_25_5.wcnf
python3 generators.py rnd -n 50 -m 200 -k 2 -o random_2cnf.wcnf
python3 generators.py sw  -n 50 -m 200 -k 3 -o smallworld.wcnf
```

Here, for `php`, the parameter `-n` is the number of holes and `-m` is the number of pigeons.

## Typical workflow

Generate an instance:

```bash
python3 generators.py php -n 5 -m 25 -o php_25_5.wcnf
```

Run CSimple:

```bash
python3 simple.py php_25_5.wcnf
```

Run CSat with heuristic 1:

```bash
python3 comp.py php_25_5.wcnf -H 1
```

Run core-guided CSat with heuristic 2:

```bash
python3 comp.py php_25_5.wcnf -H 2 -c
```

Run the Fu&Malik baseline:

```bash
python3 FuMalik.py php_25_5.wcnf
```

Run the Fu&Malik symmetry-breaking variant:

```bash
python3 FuMalikSymBreak.py php_25_5.wcnf
```

## Output

The solvers print progress information about SAT calls to standard error. These lines have the form:

```text
Instance: <file> Time: <sat-call-time> Answer: <True/False> Cost: <current-cost> Comparators: <n> Assumptions: <n>
```

At the end, the solver prints one summary line to standard output:

```text
Method: <command> Instance: <file> Cost: <optimum> Time: <sat-call-time> UNSATtime: <unsat-call-time> Comparators: <n> Cores: <n>
```

The reported `Time` is the accumulated CPU time spent inside SAT solver calls, not necessarily the total wall-clock running time of the Python process.

## Notes on the implementation

- The code assumes that all Python files are in the same directory.
- The implementations use OptiLog's interface to Glucose 4.1.
- `comp.py` uses `bitarray` to store and update the matrix of assignments efficiently.
- `FuMalik.py` and `FuMalikSymBreak.py` intentionally reject incremental mode in their current implementation.
- The code is a compact research prototype rather than a polished MaxSAT competition solver.

## BibTeX

```bibtex
@inproceedings{BonacinaLevyLiberalSAT2026,
  author    = {Ilario Bonacina and Jordi Levy and Ion Mikel Liberal},
  title     = {Beyond Core-Guided MaxSAT},
  booktitle = {29th International Conference on Theory and Applications of Satisfiability Testing (SAT 2026)},
  series    = {Leibniz International Proceedings in Informatics (LIPIcs)},
  pages     = {8:1--8:18},
  year      = {2026},
  doi       = {10.4230/LIPIcs.SAT.2026.8}
}
```

## Contact

For questions about the code or the paper, please contact the authors of the SAT 2026 paper.
