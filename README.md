# Resilience-Constrained Power System Capacity Expansion Planning Considering Cascading Failures

Fixed-scenario optimization program for the paper **"Resilience-Constrained
Power System Capacity Expansion Planning Considering Cascading Failures"**.

---

## Purpose

This program is the **fixed-scenario optimization program** of the above paper.

It solves the paper's resilience-constrained capacity expansion planning model
for a **given, fixed set of outage scenarios**: the cascading-failure scenarios
are supplied as input data, the model is built once and solved **once** to obtain
the investment plan, the restoration schedule and the risk metrics. There is no
iterative loop and no cascading-failure simulation inside the program.

The model is a single mixed-integer linear program (MILP) that jointly covers:

- **Capacity expansion planning** — new thermal / wind / PV / storage capacity
  per area, plus 24 h economic dispatch of the expanded system;
- **Black-start restoration planning** — resource deployment and a 6-step
  restoration schedule for each given outage scenario;
- **Risk constraints** — VaR and CVaR limits on load shedding;
- **Scenario coupling** — healthy buses and lines are forced off per scenario.

Objective: minimize investment cost + O&M cost + fuel / start-up cost +
probability-weighted load-shedding penalty.

Files:

| File | Content |
| --- | --- |
| `data.py` | System data, parameters, fixed outage scenarios `V_s`, solver options |
| `model.py` | `build_full_model(data, V_s)` — all constraints and the objective |
| `main.py` | Entry point — solver selection, single solve, result output |

## Environment

- **OS**: Windows / Linux / macOS
- **Python**: 3.9 or newer (developed and tested on Python 3.13)
- **Solver**: any MILP solver supported by Pyomo — COPT 8.0 (tested),
  Gurobi, HiGHS or CBC
- **Verified on**: Windows 11, Intel i7-12700 (12 physical cores),
  Python 3.13, Pyomo 6.9.5, COPT 8.0.6

## Dependencies

Python packages:

```bash
pip install numpy pyomo
```

Plus one solver and its Python interface:

```bash
pip install coptpy    # COPT   (tested)
pip install gurobipy  # Gurobi
pip install highspy   # HiGHS
```

| Package | Version used |
| --- | --- |
| `numpy` | 2.4.6 |
| `pyomo` | 6.9.5 |
| `coptpy` | COPT 8.0.6 |

COPT's Pyomo plugin (`copt*/lib/pyomo/copt_pyomo.py`) is located and loaded
automatically by the program — no manual file copying is needed.

## How to run

```bash
# Auto-select an available solver (COPT first, then Gurobi, HiGHS, CBC)
python main.py

# Use a specific solver
python main.py copt_direct
python main.py gurobi

# Use a specific solver and override the time limit (seconds)
python main.py copt_direct 600
```

The program performs a **single** optimization — load data → build model →
solve once → print results — and writes the results to `results.npy`.

Solver options are set in `data.py` (`data["solver_params"]`):
`RelGap = 0.03`, `TimeLimit = 3600`, `Threads = 16`.
