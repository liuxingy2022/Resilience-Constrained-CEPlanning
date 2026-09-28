"""main.py — Entry point (Pyomo version)

Load data -> build model -> solve -> extract and print results.

[Solve mode] Single solve, no iteration:
  * the outage scenarios V_s are fixed data (hard-coded in Section 6 of data.py)
    and are not generated dynamically inside the program;
  * build_full_model() builds every constraint at once (economic planning +
    restoration + VaR/CVaR + scenario coupling);
  * solver.solve() is called exactly once and returns the result directly --
    there is no max_iter loop and no cascading-failure simulation call.

[File layout] Three files:
    data.py   -- system data and parameters (fixed V_s, solver options)
    model.py  -- build_full_model(data, V_s): all constraints and objective
    main.py   -- entry point: solver registration/selection + solve + output

Usage:
    python main.py                   # auto-select a solver (COPT first)
    python main.py copt_direct       # pick a specific solver
    python main.py copt_direct 600   # also set the time limit (s)
"""

import importlib
import sys
from pathlib import Path

import numpy as np
import pyomo.environ as pyo

from data import get_system_data
from model import build_full_model


# ====================================================================
# Solver registration and selection
#   Pyomo 6.9.x does not ship a COPT plugin, so copt_pyomo.py bundled with
#   COPT must be imported before SolverFactory('copt_direct') can be used.
#   get_solver() auto-selects the first solver available on this machine:
#       copt_direct -> gurobi -> appsi_highs -> highs -> glpk -> cbc
# ====================================================================

_COPT_REGISTERED = None  # None = not tried yet, True/False = result


def register_copt_plugin():
    """Try to register the COPT Pyomo plugin. Returns whether it succeeded."""
    global _COPT_REGISTERED
    if _COPT_REGISTERED is not None:
        return _COPT_REGISTERED

    # 1) already installed in site-packages / current directory
    try:
        importlib.import_module("copt_pyomo")
        _COPT_REGISTERED = True
        return True
    except ImportError:
        pass

    # 2) search the usual install locations for copt*/lib/pyomo/copt_pyomo.py
    roots = [
        Path("C:/Program Files"),
        Path("D:/Program Files"),
        Path("C:/Program Files (x86)"),
        Path("D:/Program Files (x86)"),
    ]
    for root in roots:
        if not root.is_dir():
            continue
        for d in sorted(root.glob("copt*/lib/pyomo")):
            if (d / "copt_pyomo.py").is_file():
                sys.path.insert(0, str(d))
                importlib.import_module("copt_pyomo")
                _COPT_REGISTERED = True
                return True

    _COPT_REGISTERED = False
    return False


def available_solvers():
    """Return the solvers available on this machine, most preferred first."""
    register_copt_plugin()
    candidates = [
        "copt_direct",
        "gurobi",
        "gurobi_direct",
        "appsi_highs",
        "highs",
        "glpk",
        "cbc",
    ]
    ok = []
    for name in candidates:
        try:
            if pyo.SolverFactory(name).available(exception_flag=False):
                ok.append(name)
        except Exception:
            pass
    return ok


def get_solver(name=None):
    """Get a solver. With name=None, auto-select by priority.

    Returns
    -------
    (solver, name) : (SolverFactory instance, name of the solver actually used)
    """
    register_copt_plugin()

    if name is not None:
        solver = pyo.SolverFactory(name)
        if not solver.available(exception_flag=False):
            raise RuntimeError(
                f"求解器 {name!r} 不可用。可用：{available_solvers()}")
        return solver, name

    found = available_solvers()
    if not found:
        raise RuntimeError(
            "本机未找到任何可用求解器。请安装 COPT / Gurobi / HiGHS / CBC 之一。")
    return pyo.SolverFactory(found[0]), found[0]


def apply_options(solver, name, params):
    """Translate the unified parameter dict into native solver options."""
    p = dict(params)

    if name.startswith("copt"):
        mapping = {  # native COPT option names
            "RelGap": "RelGap",
            "TimeLimit": "TimeLimit",
            "Threads": "Threads",
            "Logging": "Logging",
        }
    elif name.startswith("gurobi"):
        mapping = {
            "RelGap": "MIPGap",
            "TimeLimit": "TimeLimit",
            "Threads": "Threads",
            "Logging": "LogToConsole",
        }
    elif name.startswith("appsi_highs") or name == "highs":
        mapping = {
            "RelGap": "mip_rel_gap",
            "TimeLimit": "time_limit",
            "Threads": "threads",
        }
    else:  # cbc / glpk and friends
        mapping = {
            "RelGap": "ratioGap",
            "TimeLimit": "sec",
            "Threads": "threads",
        }

    for key, opt_name in mapping.items():
        if key in p and p[key] is not None:
            solver.options[opt_name] = p[key]

    return solver


def main():
    # ================================================================
    # 1. Load system data
    # ================================================================
    print("=" * 60)
    print("  电力系统弹性规划优化 (Pyomo)")
    print("=" * 60)

    data = get_system_data()
    print(f"\n数据加载完成: {data['N']}节点, {data['N_a']}区域, {data['S']}场景")

    # ================================================================
    # 2. Get the outage scenario matrix V_s
    # ================================================================
    V_s = data["V_s"]
    print(f"场景数据 V_s: {V_s.shape}, 停电节点数/场景: {np.sum(1 - V_s, axis=1)}")

    # ================================================================
    # 3. Build the optimization model
    # ================================================================
    print("\n构建优化模型...")
    model, var = build_full_model(data, V_s)
    n_var = sum(1 for _ in model.component_data_objects(pyo.Var))
    n_bin = sum(1 for v in model.component_data_objects(pyo.Var)
                if v.is_binary())
    n_con = sum(1 for _ in model.component_data_objects(pyo.Constraint,
                                                        active=True))
    print(f"模型构建完成。变量 {n_var}（二元 {n_bin}）/ 约束 {n_con}")

    # ================================================================
    # 4. Select the solver and set its options
    # ================================================================
    solver_name = sys.argv[1] if len(sys.argv) > 1 else None
    params = dict(data["solver_params"])
    if len(sys.argv) > 2:
        params["TimeLimit"] = float(sys.argv[2])
    solver, solver_name = get_solver(solver_name)
    apply_options(solver, solver_name, params)

    print(f"\n可用求解器: {available_solvers()}")
    print(f"本次使用  : {solver_name}")
    print(f"求解参数  : {params}")

    # ================================================================
    # 5. Solve (single call, no iteration)
    # ================================================================
    print("\n开始求解（单次求解，无迭代）...")
    results = solver.solve(model, tee=True)

    term = str(results.solver.termination_condition)
    print(f"\n求解状态: {term}")

    # Read the objective value (some solvers do not fill in results.Problem)
    try:
        obj_val = pyo.value(model.OBJ)
    except Exception:
        obj_val = float("nan")

    if term in ("infeasible", "infeasibleOrUnbounded"):
        print("\n模型不可行 (INFEASIBLE)！")
        try:
            solver._solver_model.computeIIS()
            solver._solver_model.writeIIS("infeasible.ilp")
            print("不可行约束集已写入 infeasible.ilp")
        except Exception as exc:  # ignore if not COPT / unsupported by plugin
            print(f"（IIS 输出不可用：{exc}）")
        return
    if term in ("unknown",) and not np.isfinite(obj_val):
        print("未找到可行解，退出。")
        return

    # ================================================================
    # 6. Result extraction and output
    # ================================================================
    def val(x):
        return pyo.value(x)

    print("\n" + "=" * 60)
    print("  投资决策")
    print("=" * 60)

    print(f"\n目标函数值: {obj_val:,.2f}")

    print("\n新建火电容量 (MW，区域×类型):")
    print("  列: F1(150MW)  F2(300MW)  F3(300MW)  F4(600MW)")
    for ka in range(data["N_a"]):
        row = [val(model.I_F[ka, j]) for j in range(data["N_F"])]
        print(f"  区域{ka+1}: {np.round(row, 2)}")

    print("\n新建风电容量 (MW，各区域):")
    for ka in range(data["N_a"]):
        print(f"  区域{ka+1}: {val(model.I_W[ka]):.1f}")

    print("\n新建光伏容量 (MW，各区域):")
    for ka in range(data["N_a"]):
        print(f"  区域{ka+1}: {val(model.I_R[ka]):.1f}")

    print("\n新建储能额定功率 (MW，区域×类型 [构网型, 跟网型]):")
    for ka in range(data["N_a"]):
        row = [val(model.I_ESS_P[ka, k]) for k in range(data["N_ESS"])]
        print(f"  区域{ka+1}: {np.round(row, 2)}")

    print("\n对应储能额定能量 (MWh, = 4h × 功率):")
    for ka in range(data["N_a"]):
        row = [4 * val(model.I_ESS_P[ka, k]) for k in range(data["N_ESS"])]
        print(f"  区域{ka+1}: {np.round(row, 2)}")

    # ---- load shedding ----
    print("\n" + "=" * 60)
    print("  各场景切负荷量 (MW·时步)")
    print("=" * 60)
    for s in range(data["S"]):
        print(f"  场景{s+1:2d}: {val(model.p_shed[s]):10.2f}")

    # ---- energization status of buses in restoration scenario 1 ----
    print("\n" + "=" * 60)
    print("  恢复场景1 — 节点在位状态")
    print("=" * 60)
    for t in range(data["T_R"]):
        nodes_on = [j + 1 for j in range(data["N"])
                    if val(model.En_V[0, t, j]) > 0.5]
        print(f"  t={t+1}: 通电节点 = {nodes_on}")

    # ---- storage SOC trajectory (scenario 1, type 1) ----
    print("\n" + "=" * 60)
    print("  恢复场景1 — 储能SOC轨迹 (类型1=构网型50MW，各节点汇总)")
    print("=" * 60)
    for t in range(data["T_R"]):
        soc_val = sum(val(model.SOC_ESS_R[0, 0, t, nz, j])
                      for nz in range(data["N_Z_ESS"])
                      for j in range(data["N"]))
        print(f"  t={t+1:2d}: {soc_val:.2f} MWh")

    # ---- storage deployment locations ----
    print("\n" + "=" * 60)
    print("  储能部署位置")
    print("=" * 60)
    for k in range(data["N_ESS_R"]):
        nodes_with_ess = [j + 1 for nz in range(data["N_Z_ESS"])
                          for j in range(data["N"])
                          if val(model.Dep_ESS[k, nz, j]) > 0.5]
        print(f"  类型{k+1} ({data['p_ESS_unit_max'][k]}MW): "
              f"节点 = {sorted(set(nodes_with_ess))}")

    # ---- cost breakdown ----
    print("\n" + "=" * 60)
    print("  成本分解")
    print("=" * 60)
    print(f"  投资成本 C_Inv: {val(var['C_Inv']):,.2f}")
    print(f"  运维成本 C_OM:  {val(var['C_OM']):,.2f}")
    print(f"  运行成本 C_V:   {val(var['C_V']):,.2f}")
    print(f"  切负荷惩罚:      {val(var['shed_penalty']):,.2f}")

    # ================================================================
    # 7. Save results
    # ================================================================
    N_a, N_F, N_ESS = data["N_a"], data["N_F"], data["N_ESS"]
    N, N_Z, N_Z_ESS, N_ESS_R = (data["N"], data["N_Z"], data["N_Z_ESS"],
                                data["N_ESS_R"])

    results = {
        "I_F": np.array([[val(model.I_F[i, j]) for j in range(N_F)]
                         for i in range(N_a)]),
        "I_W": np.array([[val(model.I_W[i])] for i in range(N_a)]),
        "I_R": np.array([[val(model.I_R[i])] for i in range(N_a)]),
        "I_ESS_P": np.array([[val(model.I_ESS_P[i, k]) for k in range(N_ESS)]
                             for i in range(N_a)]),
        "Dep_F": {i: np.array([[val(model.Dep_F[i, nz, j])
                                for j in range(N)] for nz in range(N_Z)])
                  for i in range(N_F)},
        "Dep_W": np.array([[val(model.Dep_W[nz, j]) for j in range(N)]
                           for nz in range(N_Z)]),
        "Dep_R": np.array([[val(model.Dep_R[nz, j]) for j in range(N)]
                           for nz in range(N_Z)]),
        "Dep_ESS": {k: np.array([[val(model.Dep_ESS[k, nz, j])
                                  for j in range(N)] for nz in range(N_Z_ESS)])
                    for k in range(N_ESS_R)},
        "p_shed": {s: val(model.p_shed[s]) for s in range(data["S"])},
        "En_V": {s: np.array([[val(model.En_V[s, t, j]) for j in range(N)]
                              for t in range(data["T_R"])])
                 for s in range(data["S"])},
        "obj_val": obj_val,
        "solver": solver_name,
    }
    np.save("results.npy", results, allow_pickle=True)
    print(f"\n结果已保存至 results.npy")

    print("\n" + "=" * 60)
    print("  求解完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
