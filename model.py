"""model.py — Main optimization model (Pyomo version)

Builds the integrated economic planning + black-start restoration + CVaR Pyomo
model. Corresponds to Chapters 3-5 and the Con_RR part of Chapter 6 of the
original MATLAB program.

Core function: build_full_model(data, V_s) -> (model, var_dict)

Differences from the gurobipy version (semantics identical, modeling API only):
  * gp.Model / addMVar    ->  pyo.ConcreteModel / pyo.Var (multi-index)
  * per-constraint loops  ->  Constraint(index_set, rule=...) vectorized
  * ranged inequalities with VARIABLE bounds (e.g. -M*z <= x <= M*z) must be
    split into two constraints; otherwise Pyomo cannot normalize them and a
    direct solver rejects the model (see get_solver in main.py).
"""

import numpy as np
import pyomo.environ as pyo


def build_full_model(data, V_s):
    """Build the complete single-solve optimization model.

    Parameters
    ----------
    data : dict
        System parameters returned by data.get_system_data().
    V_s : np.ndarray, shape (S, N)
        Scenario survival matrix. V_s[s, j] = 1 means bus j is healthy
        (not in the outaged zone) in scenario s.

    Returns
    -------
    model : pyo.ConcreteModel
        Pyomo model containing all constraints and the objective (unsolved).
    var : dict
        References to the key decision variables and objective components,
        used by main.py to extract the results.
    """
    # ================================================================
    # 0. Parameter extraction
    # ================================================================
    N = data["N"]
    N_a = data["N_a"]
    N_F = data["N_F"]
    N_ESS = data["N_ESS"]
    T = data["T"]
    S = data["S"]
    T_R = data["T_R"]
    N_Z = data["N_Z"]
    N_Z_ESS = data["N_Z_ESS"]
    N_ESS_R = data["N_ESS_R"]

    BusArea = data["BusArea"]
    C = data["C"]
    NL = C.shape[0]

    P_S = data["P_S"]
    M_dc = data["M_dc"]
    b_line = data["b_line"]
    theta_max = data["theta_max"]
    p_Line_max = data["p_Line_max"]
    bus_ref = data["bus_ref"]
    p_D_mat = data["p_D_mat"]
    M_big = data["M_big"]

    # Branch incidence lists (precomputed, used by R9 / R15)
    lines_out_of = [[li for li in range(NL) if C[li, 0] == j] for j in range(N)]
    lines_into = [[li for li in range(NL) if C[li, 1] == j] for j in range(N)]

    # ---- Create the model and the index sets ----
    m = pyo.ConcreteModel(name="PlanAndResilience")
    m.IA = pyo.Set(initialize=range(N_a))          # areas
    m.IF = pyo.Set(initialize=range(N_F))          # thermal unit types
    m.IE = pyo.Set(initialize=range(N_ESS))        # storage types (economic)
    m.IT = pyo.Set(initialize=range(T))            # economic operation steps (24h)
    m.ITR = pyo.Set(initialize=range(T_R))         # restoration time steps
    m.IB = pyo.Set(initialize=range(N))            # buses
    m.IL = pyo.Set(initialize=range(NL))           # branches
    m.IS = pyo.Set(initialize=range(S))            # scenarios
    m.IZ = pyo.Set(initialize=range(N_Z))          # thermal/wind/PV slots per bus
    m.IZE = pyo.Set(initialize=range(N_Z_ESS))     # storage slots per bus
    m.IER = pyo.Set(initialize=range(N_ESS_R))     # storage device types (restoration)

    var = {}

    # ================================================================
    # Part 1 — Economic planning
    # ================================================================

    # ---- Investment variables ----
    m.I_F = pyo.Var(m.IA, m.IF, domain=pyo.NonNegativeReals)
    m.I_W = pyo.Var(m.IA, domain=pyo.NonNegativeReals)
    m.I_R = pyo.Var(m.IA, domain=pyo.NonNegativeReals)
    m.I_ESS_P = pyo.Var(m.IA, m.IE, domain=pyo.NonNegativeReals)

    # ---- Operating variables (24h) ----
    m.P_F = pyo.Var(m.IT, m.IA, m.IF, domain=pyo.NonNegativeReals)
    m.P_F_up = pyo.Var(m.IT, m.IA, m.IF, domain=pyo.NonNegativeReals)
    m.START_F = pyo.Var(m.IT, m.IA, m.IF, domain=pyo.NonNegativeReals)
    m.SHUT_F = pyo.Var(m.IT, m.IA, m.IF, domain=pyo.NonNegativeReals)

    m.P_W = pyo.Var(m.IT, m.IA, domain=pyo.NonNegativeReals)
    m.P_R = pyo.Var(m.IT, m.IA, domain=pyo.NonNegativeReals)
    m.P_W_up = pyo.Var(m.IT, m.IA, domain=pyo.NonNegativeReals)
    m.P_R_up = pyo.Var(m.IT, m.IA, domain=pyo.NonNegativeReals)

    m.P_ESS_ch = pyo.Var(m.IT, m.IA, m.IE, domain=pyo.NonNegativeReals)
    m.P_ESS_dis = pyo.Var(m.IT, m.IA, m.IE, domain=pyo.NonNegativeReals)
    m.SOC_ESS = pyo.Var(m.IT, m.IA, m.IE, domain=pyo.NonNegativeReals)

    m.P_Deli = pyo.Var(m.IT, m.IA, m.IA, domain=pyo.Reals)

    var["I_F"] = m.I_F
    var["I_W"] = m.I_W
    var["I_R"] = m.I_R
    var["I_ESS_P"] = m.I_ESS_P
    var["P_F"] = m.P_F
    var["P_W"] = m.P_W
    var["P_R"] = m.P_R
    var["SOC_ESS"] = m.SOC_ESS

    # ---- Existing installed capacity ----
    I_F0 = data["I_F0"]
    I_W0 = data["I_W0"].reshape(N_a)
    I_R0 = data["I_R0"].reshape(N_a)

    # ---- (4)(5)(6)(N1) output capped by new + existing total capacity ----
    m.N1_PF = pyo.Constraint(
        m.IT, m.IA, m.IF,
        rule=lambda m, t, i, j: m.P_F[t, i, j] <= m.P_F_up[t, i, j])
    m.N1_PF_cap = pyo.Constraint(
        m.IT, m.IA, m.IF,
        rule=lambda m, t, i, j: m.P_F_up[t, i, j] <= m.I_F[i, j] + I_F0[i, j])

    m.N1_PW = pyo.Constraint(
        m.IT, m.IA, rule=lambda m, t, i: m.P_W[t, i] <= m.P_W_up[t, i])
    m.N1_PW_cap = pyo.Constraint(
        m.IT, m.IA, rule=lambda m, t, i: m.P_W_up[t, i] <= m.I_W[i] + I_W0[i])

    m.N1_PR = pyo.Constraint(
        m.IT, m.IA, rule=lambda m, t, i: m.P_R[t, i] <= m.P_R_up[t, i])
    m.N1_PR_cap = pyo.Constraint(
        m.IT, m.IA, rule=lambda m, t, i: m.P_R_up[t, i] <= m.I_R[i] + I_R0[i])

    # ---- (N2) storage charge/discharge power limits ----
    m.N2_ch = pyo.Constraint(
        m.IT, m.IA, m.IE,
        rule=lambda m, t, i, k: m.P_ESS_ch[t, i, k] <= m.I_ESS_P[i, k])
    m.N2_dis = pyo.Constraint(
        m.IT, m.IA, m.IE,
        rule=lambda m, t, i, k: m.P_ESS_dis[t, i, k] <= m.I_ESS_P[i, k])

    # ---- (N3) SOC dynamics (DeltaT = 1h) ----
    SOC_ini_ratio = data["SOC_ini_ratio"]
    T_ESS_val = data["T_ESS"]
    eta_ch = data["eta_ch"]
    eta_dis = data["eta_dis"]

    m.N3_SOC_0 = pyo.Constraint(
        m.IA, m.IE,
        rule=lambda m, i, k: m.SOC_ESS[0, i, k]
        == SOC_ini_ratio * T_ESS_val * m.I_ESS_P[i, k]
        + eta_ch * m.P_ESS_ch[0, i, k]
        - (1.0 / eta_dis) * m.P_ESS_dis[0, i, k])

    m.N3_SOC_t = pyo.Constraint(
        range(1, T), m.IA, m.IE,
        rule=lambda m, t, i, k: m.SOC_ESS[t, i, k]
        == m.SOC_ESS[t - 1, i, k]
        + eta_ch * m.P_ESS_ch[t, i, k]
        - (1.0 / eta_dis) * m.P_ESS_dis[t, i, k])

    # ---- (N4) SOC bounds ----
    SOC_min_ratio = data["SOC_min_ratio"]
    SOC_max_ratio = data["SOC_max_ratio"]
    m.N4_SOC_lo = pyo.Constraint(
        m.IT, m.IA, m.IE,
        rule=lambda m, t, i, k: SOC_min_ratio * T_ESS_val * m.I_ESS_P[i, k]
        <= m.SOC_ESS[t, i, k])
    m.N4_SOC_hi = pyo.Constraint(
        m.IT, m.IA, m.IE,
        rule=lambda m, t, i, k: m.SOC_ESS[t, i, k]
        <= SOC_max_ratio * T_ESS_val * m.I_ESS_P[i, k])

    # ---- (N5) end-of-day SOC returns to its initial value ----
    m.N5 = pyo.Constraint(
        m.IA, m.IE,
        rule=lambda m, i, k: m.SOC_ESS[T - 1, i, k]
        == SOC_ini_ratio * T_ESS_val * m.I_ESS_P[i, k])

    # ---- (7) area power balance (including net storage power) ----
    P_D = data["P_D"]

    def rule_area_balance(m, i_a, t):
        return (
            pyo.quicksum(m.P_F[t, i_a, j] for j in range(N_F))
            + m.P_W[t, i_a] + m.P_R[t, i_a]
            + pyo.quicksum(m.P_ESS_dis[t, i_a, k] - m.P_ESS_ch[t, i_a, k]
                           for k in range(N_ESS))
            + pyo.quicksum(m.P_Deli[t, i_a, jj] for jj in range(N_a))
            == P_D[t, i_a]
        )

    m.C7_balance = pyo.Constraint(m.IA, m.IT, rule=rule_area_balance)

    # ---- (8) tie-line limits and antisymmetry ----
    L_down, L_up = data["L_down"], data["L_up"]
    m.C8_lo = pyo.Constraint(
        m.IT, m.IA, m.IA,
        rule=lambda m, t, i, j: m.P_Deli[t, i, j] >= L_down[i, j])
    m.C8_hi = pyo.Constraint(
        m.IT, m.IA, m.IA,
        rule=lambda m, t, i, j: m.P_Deli[t, i, j] <= L_up[i, j])
    m.C8_anti = pyo.Constraint(
        m.IT, m.IA, m.IA,
        rule=lambda m, t, i, j: m.P_Deli[t, i, j] == -m.P_Deli[t, j, i])

    # ---- (9)(10) thermal start-up/shut-down logic and limits ----
    m.C9_ramp = pyo.Constraint(
        range(1, T), m.IA, m.IF,
        rule=lambda m, t, i, j: m.P_F[t, i, j] - m.P_F[t - 1, i, j]
        == m.START_F[t, i, j] - m.SHUT_F[t, i, j])
    m.C10_start = pyo.Constraint(
        m.IT, m.IA, m.IF,
        rule=lambda m, t, i, j: m.START_F[t, i, j] <= m.I_F[i, j] + I_F0[i, j])
    m.C10_shut = pyo.Constraint(
        m.IT, m.IA, m.IF,
        rule=lambda m, t, i, j: m.SHUT_F[t, i, j] <= m.I_F[i, j] + I_F0[i, j])

    # ---- (18) thermal ramp limits during normal operation ----
    #      -rho_down_i * dt * Pbar^F_{i,k,t} <= P^F_{i,k,t} - P^F_{i,k,t-1}
    #                                        <= rho_up_i * dt * Pbar^F_{i,k,t}
    # Pbar^F_{i,k,t} (online capacity) is represented here by P_F_up, the
    # variable that already caps P_F and is bounded by the installed capacity
    # I_F + I_F0 (see N1 above). Index mapping: our P_F[t, i, j] has i = area,
    # j = thermal type, so rho_up / rho_down are indexed by j.
    rho_up = data["rho_up"]
    rho_down = data["rho_down"]
    dt_h = data["DeltaT"]

    m.C18_ramp_lo = pyo.Constraint(
        range(1, T), m.IA, m.IF,
        rule=lambda m, t, i, j: m.P_F[t, i, j] - m.P_F[t - 1, i, j]
        >= -rho_down[j] * dt_h * m.P_F_up[t, i, j])
    m.C18_ramp_hi = pyo.Constraint(
        range(1, T), m.IA, m.IF,
        rule=lambda m, t, i, j: m.P_F[t, i, j] - m.P_F[t - 1, i, j]
        <= rho_up[j] * dt_h * m.P_F_up[t, i, j])

    # ---- Cost components ----
    c_Inv_F = data["c_Inv_F"]
    c_Inv_W = data["c_Inv_W"]
    c_Inv_R = data["c_Inv_R"]
    c_Inv_ESS = data["c_Inv_ESS"]
    c_OM_F = data["c_OM_F"]
    c_OM_W = data["c_OM_W"]
    c_OM_R = data["c_OM_R"]
    c_OM_ESS = data["c_OM_ESS"]
    c_opera_F = data["c_opera_F"]
    c_SD_F = data["c_SD_F"]

    C_Inv = (
        pyo.quicksum(c_Inv_F[i, j] * m.I_F[i, j]
                     for i in range(N_a) for j in range(N_F))
        + pyo.quicksum(c_Inv_W[i, 0] * m.I_W[i] for i in range(N_a))
        + pyo.quicksum(c_Inv_R[i, 0] * m.I_R[i] for i in range(N_a))
        + pyo.quicksum(c_Inv_ESS[i, k] * m.I_ESS_P[i, k]
                       for i in range(N_a) for k in range(N_ESS))
    )

    C_OM = (
        pyo.quicksum(c_OM_F[i, j] * (m.I_F[i, j] + I_F0[i, j])
                     for i in range(N_a) for j in range(N_F))
        + pyo.quicksum(c_OM_W[i, 0] * (m.I_W[i] + I_W0[i]) for i in range(N_a))
        + pyo.quicksum(c_OM_R[i, 0] * (m.I_R[i] + I_R0[i]) for i in range(N_a))
        + pyo.quicksum(c_OM_ESS[i, k] * m.I_ESS_P[i, k]
                       for i in range(N_a) for k in range(N_ESS))
    )

    C_V = pyo.quicksum(
        pyo.quicksum(c_opera_F[i, j] * m.P_F[t, i, j]
                     for i in range(N_a) for j in range(N_F))
        + pyo.quicksum(c_SD_F[i, j] * m.START_F[t, i, j]
                       for i in range(N_a) for j in range(N_F))
        for t in range(T)
    )

    # ================================================================
    # Part 2 — Restoration resilience planning
    # ================================================================

    p_F_max = data["p_F_max"]
    p_W_max = data["p_W_max"]
    p_R_max = data["p_R_max"]
    Ramp = data["Ramp"]
    TCR = data["TCR"]
    PCR = data["PCR"]

    # ---- Deployment variables (binary) ----
    m.Dep_F = pyo.Var(m.IF, m.IZ, m.IB, domain=pyo.Binary)
    m.Dep_W = pyo.Var(m.IZ, m.IB, domain=pyo.Binary)
    m.Dep_R = pyo.Var(m.IZ, m.IB, domain=pyo.Binary)
    m.Dep_ESS = pyo.Var(m.IER, m.IZE, m.IB, domain=pyo.Binary)

    Dep_F_0 = data["Dep_F_0"]
    Dep_W_0 = data["Dep_W_0"]
    Dep_R_0 = data["Dep_R_0"]

    var["Dep_F"] = m.Dep_F
    var["Dep_W"] = m.Dep_W
    var["Dep_R"] = m.Dep_R
    var["Dep_ESS"] = m.Dep_ESS

    # ---- Operating variables (per scenario) ----
    m.p_shed = pyo.Var(m.IS, domain=pyo.NonNegativeReals)
    m.p_load = pyo.Var(m.IS, m.ITR, m.IB, domain=pyo.NonNegativeReals)
    m.P_Line = pyo.Var(m.IS, m.ITR, m.IL, domain=pyo.Reals)
    m.En_L = pyo.Var(m.IS, m.ITR, m.IL, domain=pyo.Binary)
    m.En_V = pyo.Var(m.IS, m.ITR, m.IB, domain=pyo.Binary)
    m.p_fLine = pyo.Var(m.IS, m.ITR, m.IL, domain=pyo.Reals)
    m.theta = pyo.Var(m.IS, m.ITR, m.IB, domain=pyo.Reals)

    m.En_F = pyo.Var(m.IF, m.IS, m.ITR, m.IZ, m.IB, domain=pyo.Binary)
    m.P_F_R = pyo.Var(m.IF, m.IS, m.ITR, m.IZ, m.IB, domain=pyo.NonNegativeReals)
    m.P_W_R = pyo.Var(m.IS, m.ITR, m.IZ, m.IB, domain=pyo.NonNegativeReals)
    m.P_R_R = pyo.Var(m.IS, m.ITR, m.IZ, m.IB, domain=pyo.NonNegativeReals)

    m.En_ESS = pyo.Var(m.IER, m.IS, m.ITR, m.IZE, m.IB, domain=pyo.Binary)
    m.P_ESS_ch_R = pyo.Var(m.IER, m.IS, m.ITR, m.IZE, m.IB,
                           domain=pyo.NonNegativeReals)
    m.P_ESS_dis_R = pyo.Var(m.IER, m.IS, m.ITR, m.IZE, m.IB,
                            domain=pyo.NonNegativeReals)
    m.SOC_ESS_R = pyo.Var(m.IER, m.IS, m.ITR, m.IZE, m.IB,
                          domain=pyo.NonNegativeReals)

    var["p_shed"] = m.p_shed
    var["En_V"] = m.En_V
    var["SOC_ESS_R"] = m.SOC_ESS_R
    var["P_F_R"] = m.P_F_R
    var["P_W_R"] = m.P_W_R
    var["P_R_R"] = m.P_R_R

    # ---- R1: area resource aggregation -- thermal
    #      (equality, as in the paper formulation:
    #       sum_{j in V_k} sum_n h^F_{i,j,n} p^F,max_i = I^F_{i,k}, for all i,k)
    def rule_R1_F(m, ka, j):
        return (pyo.quicksum(m.Dep_F[j, nz, n] * p_F_max[j]
                             for nz in range(N_Z) for n in BusArea[ka])
                == m.I_F[ka, j])

    # ---- R1: area resource aggregation -- wind ----
    def rule_R1_W(m, ka):
        return (pyo.quicksum(m.Dep_W[nz, n] * p_W_max
                             for nz in range(N_Z) for n in BusArea[ka])
                == m.I_W[ka])

    # ---- R1: area resource aggregation -- PV ----
    def rule_R1_R(m, ka):
        return (pyo.quicksum(m.Dep_R[nz, n] * p_R_max
                             for nz in range(N_Z) for n in BusArea[ka])
                == m.I_R[ka])

    m.R1_F = pyo.Constraint(m.IA, m.IF, rule=rule_R1_F)
    m.R1_W = pyo.Constraint(m.IA, rule=rule_R1_W)
    m.R1_R = pyo.Constraint(m.IA, rule=rule_R1_R)

    # ---- R1-ESS: area resource aggregation -- storage (equality) ----
    p_ESS_unit_max = data["p_ESS_unit_max"]

    def rule_R1_ESS(m, ka, k):
        return (pyo.quicksum(m.Dep_ESS[k, nz, n] * p_ESS_unit_max[k]
                             for nz in range(N_Z_ESS) for n in BusArea[ka])
                == m.I_ESS_P[ka, k])

    m.R1_ESS = pyo.Constraint(m.IA, m.IER, rule=rule_R1_ESS)

    # ---- R3: number of units that can be started <= number deployed ----
    m.R3_F = pyo.Constraint(
        m.IF, m.IS, m.ITR, m.IZ, m.IB,
        rule=lambda m, i, s, t, nz, j: m.En_F[i, s, t, nz, j]
        <= m.Dep_F[i, nz, j] + Dep_F_0[i][nz, j])

    m.R3_W = pyo.Constraint(
        m.IS, m.ITR, m.IZ, m.IB,
        rule=lambda m, s, t, nz, j: m.P_W_R[s, t, nz, j]
        <= (m.Dep_W[nz, j] + Dep_W_0[nz, j]) * p_W_max)

    m.R3_R = pyo.Constraint(
        m.IS, m.ITR, m.IZ, m.IB,
        rule=lambda m, s, t, nz, j: m.P_R_R[s, t, nz, j]
        <= (m.Dep_R[nz, j] + Dep_R_0[nz, j]) * p_R_max)

    # ---- R3-ESS: number of storage units that can be started <= deployed ----
    m.R3_ESS = pyo.Constraint(
        m.IER, m.IS, m.ITR, m.IZE, m.IB,
        rule=lambda m, k, s, t, nz, j: m.En_ESS[k, s, t, nz, j]
        <= m.Dep_ESS[k, nz, j])

    # ---- R4: thermal output limited by the cold-start time ----
    def rule_R4(m, i, s, t, nz, j):
        tcri = int(TCR[i])
        if tcri == 0:
            return m.P_F_R[i, s, t, nz, j] <= m.En_F[i, s, t, nz, j] * p_F_max[i]
        # TCR >= 1: force zero output while t < TCR
        # (the original program's R4 supplement for t = 0)
        if t < tcri:
            return m.P_F_R[i, s, t, nz, j] <= 0
        # Remaining steps: output limited by the unit state at start time t0
        for t0 in range(T_R - tcri):
            if t0 <= t <= t0 + tcri:
                return (m.P_F_R[i, s, t, nz, j]
                        <= m.En_F[i, s, t0, nz, j] * p_F_max[i])
        return pyo.Constraint.Skip

    m.R4 = pyo.Constraint(m.IF, m.IS, m.ITR, m.IZ, m.IB, rule=rule_R4)

    # ---- R6: thermal ramp constraints ----
    m.R6_t0 = pyo.Constraint(
        m.IF, m.IS, m.IZ, m.IB,
        rule=lambda m, i, s, nz, j: m.P_F_R[i, s, 0, nz, j] <= Ramp[i])

    m.R6_lo = pyo.Constraint(
        m.IF, m.IS, range(1, T_R), m.IZ, m.IB,
        rule=lambda m, i, s, t, nz, j: m.P_F_R[i, s, t, nz, j]
        - m.P_F_R[i, s, t - 1, nz, j] >= -Ramp[i])

    m.R6_hi = pyo.Constraint(
        m.IF, m.IS, range(1, T_R), m.IZ, m.IB,
        rule=lambda m, i, s, t, nz, j: m.P_F_R[i, s, t, nz, j]
        - m.P_F_R[i, s, t - 1, nz, j] <= Ramp[i])

    # ---- R10: line flow limited by the energization state
    #      (ranged inequality -> split into two) ----
    m.R10_lo = pyo.Constraint(
        m.IS, m.ITR, m.IL,
        rule=lambda m, s, t, li: m.P_Line[s, t, li]
        >= -p_Line_max * m.En_L[s, t, li])
    m.R10_hi = pyo.Constraint(
        m.IS, m.ITR, m.IL,
        rule=lambda m, s, t, li: m.P_Line[s, t, li]
        <= p_Line_max * m.En_L[s, t, li])

    # ---- R9: nodal power balance (including net storage power) ----
    def rule_R9(m, s, t, j):
        gen_inj = pyo.quicksum(
            m.P_F_R[i, s, t, nz, j] - PCR[i] * m.En_F[i, s, t, nz, j]
            for nz in range(N_Z) for i in range(N_F))
        renew_inj = pyo.quicksum(
            m.P_W_R[s, t, nz, j] + m.P_R_R[s, t, nz, j]
            for nz in range(N_Z))
        ess_dis = pyo.quicksum(m.P_ESS_dis_R[k, s, t, nz, j]
                               for nz in range(N_Z_ESS) for k in range(N_ESS_R))
        ess_ch = pyo.quicksum(m.P_ESS_ch_R[k, s, t, nz, j]
                              for nz in range(N_Z_ESS) for k in range(N_ESS_R))
        line_out = pyo.quicksum(m.P_Line[s, t, li] for li in lines_out_of[j])
        line_in = pyo.quicksum(m.P_Line[s, t, li] for li in lines_into[j])
        return (gen_inj + renew_inj + ess_dis - ess_ch - m.p_load[s, t, j]
                == line_out - line_in)

    m.R9 = pyo.Constraint(m.IS, m.ITR, m.IB, rule=rule_R9)

    # ---- R10-DC: flow vs. angle difference, linearized by Big-M switching ----
    m.R10DC_hi = pyo.Constraint(
        m.IS, m.IL, m.ITR,
        rule=lambda m, s, li, t: (
            m.P_Line[s, t, li]
            - b_line[li] * (m.theta[s, t, C[li, 0]] - m.theta[s, t, C[li, 1]])
            <= M_dc[li] * (1 - m.En_L[s, t, li])))
    m.R10DC_lo = pyo.Constraint(
        m.IS, m.IL, m.ITR,
        rule=lambda m, s, li, t: (
            m.P_Line[s, t, li]
            - b_line[li] * (m.theta[s, t, C[li, 0]] - m.theta[s, t, C[li, 1]])
            >= -M_dc[li] * (1 - m.En_L[s, t, li])))

    # ---- R10-DC: bus angle feasible region ----
    for s in range(S):
        for t in range(T_R):
            for j in range(N):
                m.theta[s, t, j].setlb(-theta_max)
                m.theta[s, t, j].setub(theta_max)
    m.R10DC_ref = pyo.Constraint(
        m.IS, m.ITR, rule=lambda m, s, t: m.theta[s, t, bus_ref] == 0)

    # ---- R11: load restoration limited by bus energization (incl. storage) ----
    m.R11_EnF = pyo.Constraint(
        m.IF, m.IS, m.ITR, m.IZ, m.IB,
        rule=lambda m, i, s, t, nz, j: m.En_F[i, s, t, nz, j] <= m.En_V[s, t, j])

    # ---- R12: restored load <= energization state x bus load ----
    m.R12 = pyo.Constraint(
        m.IS, m.ITR, m.IB,
        rule=lambda m, s, t, j: m.p_load[s, t, j]
        <= m.En_V[s, t, j] * p_D_mat[t, j])

    m.R11_EnESS = pyo.Constraint(
        m.IER, m.IS, m.ITR, m.IZE, m.IB,
        rule=lambda m, k, s, t, nz, j: m.En_ESS[k, s, t, nz, j] <= m.En_V[s, t, j])

    # ---- R17: monotonicity of load restoration ----
    m.R17 = pyo.Constraint(
        m.IS, range(1, T_R), m.IB,
        rule=lambda m, s, t, j: m.p_load[s, t, j] >= m.p_load[s, t - 1, j])

    # ---- R13/R14: line energization constraints ----
    def rule_R13(m, s, t, li):
        if t == 0:
            return m.En_L[s, 0, li] == 0
        return (m.En_L[s, t, li]
                <= m.En_V[s, t - 1, C[li, 0]] + m.En_V[s, t - 1, C[li, 1]])

    m.R13 = pyo.Constraint(m.IS, m.ITR, m.IL, rule=rule_R13)

    # ---- R15/R16: virtual power flow (auxiliary connectivity check) ----
    ESS_gridforming = data["ESS_gridforming"]

    m.R16_lo = pyo.Constraint(
        m.IS, m.ITR, m.IL,
        rule=lambda m, s, t, li: m.p_fLine[s, t, li]
        >= -M_big * m.En_L[s, t, li])
    m.R16_hi = pyo.Constraint(
        m.IS, m.ITR, m.IL,
        rule=lambda m, s, t, li: m.p_fLine[s, t, li]
        <= M_big * m.En_L[s, t, li])

    def rule_R15(m, s, t, j):
        source_count = pyo.quicksum(
            m.En_F[i, s, t, nz, j] for i in range(N_F) for nz in range(N_Z))
        source_count += pyo.quicksum(
            m.En_ESS[k, s, t, nz, j]
            for k in range(N_ESS_R) if ESS_gridforming[k] == 1
            for nz in range(N_Z_ESS))
        flow = (pyo.quicksum(m.p_fLine[s, t, li] for li in lines_out_of[j])
                - pyo.quicksum(m.p_fLine[s, t, li] for li in lines_into[j]))
        return (flow >= -M_big * source_count - m.En_V[s, t, j])

    def rule_R15b(m, s, t, j):
        source_count = pyo.quicksum(
            m.En_F[i, s, t, nz, j] for i in range(N_F) for nz in range(N_Z))
        source_count += pyo.quicksum(
            m.En_ESS[k, s, t, nz, j]
            for k in range(N_ESS_R) if ESS_gridforming[k] == 1
            for nz in range(N_Z_ESS))
        flow = (pyo.quicksum(m.p_fLine[s, t, li] for li in lines_out_of[j])
                - pyo.quicksum(m.p_fLine[s, t, li] for li in lines_into[j]))
        return (flow <= M_big * source_count - m.En_V[s, t, j])

    m.R15_lo = pyo.Constraint(m.IS, m.ITR, m.IB, rule=rule_R15)
    m.R15_hi = pyo.Constraint(m.IS, m.ITR, m.IB, rule=rule_R15b)

    # ---- R17-1: storage SOC dynamics (restoration scenarios) ----
    SOC_R_ini_ratio = data["SOC_R_ini_ratio"]
    e_ESS_unit_max = data["e_ESS_unit_max"]
    eta_ch_R = data["eta_ch_R"]
    eta_dis_R = data["eta_dis_R"]

    m.R17_1_t0 = pyo.Constraint(
        m.IER, m.IS, m.IZE, m.IB,
        rule=lambda m, k, s, nz, j: m.SOC_ESS_R[k, s, 0, nz, j]
        == SOC_R_ini_ratio * e_ESS_unit_max[k] * m.En_ESS[k, s, 0, nz, j]
        + eta_ch_R * m.P_ESS_ch_R[k, s, 0, nz, j]
        - (1.0 / eta_dis_R) * m.P_ESS_dis_R[k, s, 0, nz, j])

    m.R17_1_t = pyo.Constraint(
        m.IER, m.IS, range(1, T_R), m.IZE, m.IB,
        rule=lambda m, k, s, t, nz, j: m.SOC_ESS_R[k, s, t, nz, j]
        == m.SOC_ESS_R[k, s, t - 1, nz, j]
        + eta_ch_R * m.P_ESS_ch_R[k, s, t, nz, j]
        - (1.0 / eta_dis_R) * m.P_ESS_dis_R[k, s, t, nz, j])

    # ---- R17-2: storage SOC bounds ----
    SOC_R_min_ratio = data["SOC_R_min_ratio"]
    SOC_R_max_ratio = data["SOC_R_max_ratio"]

    m.R17_2_lo = pyo.Constraint(
        m.IER, m.IS, m.ITR, m.IZE, m.IB,
        rule=lambda m, k, s, t, nz, j: (
            SOC_R_min_ratio * e_ESS_unit_max[k] * m.En_ESS[k, s, t, nz, j]
            <= m.SOC_ESS_R[k, s, t, nz, j]))
    m.R17_2_hi = pyo.Constraint(
        m.IER, m.IS, m.ITR, m.IZE, m.IB,
        rule=lambda m, k, s, t, nz, j: (
            m.SOC_ESS_R[k, s, t, nz, j]
            <= SOC_R_max_ratio * e_ESS_unit_max[k] * m.En_ESS[k, s, t, nz, j]))

    # ---- R17-3: storage charge/discharge power limits ----
    m.R17_3_ch = pyo.Constraint(
        m.IER, m.IS, m.ITR, m.IZE, m.IB,
        rule=lambda m, k, s, t, nz, j: m.P_ESS_ch_R[k, s, t, nz, j]
        <= p_ESS_unit_max[k] * m.En_ESS[k, s, t, nz, j])
    m.R17_3_dis = pyo.Constraint(
        m.IER, m.IS, m.ITR, m.IZE, m.IB,
        rule=lambda m, k, s, t, nz, j: m.P_ESS_dis_R[k, s, t, nz, j]
        <= p_ESS_unit_max[k] * m.En_ESS[k, s, t, nz, j])

    # ================================================================
    # Part 3 — VaR + CVaR dual risk constraints
    # ================================================================

    m.ZT = pyo.Var(m.IS, domain=pyo.Binary)
    Var_val = data["Var"]
    a_Var = data["a_Var"]
    M_big_var = data["M_big_var"]

    m.eta_var = pyo.Var(domain=pyo.Reals)
    m.u_var = pyo.Var(m.IS, domain=pyo.NonNegativeReals)

    var["ZT"] = m.ZT
    var["eta"] = m.eta_var

    # VaR constraints
    m.VaR_s = pyo.Constraint(
        m.IS, rule=lambda m, s: m.p_shed[s] - M_big_var * m.ZT[s] <= Var_val)
    m.VaR_prob = pyo.Constraint(
        expr=pyo.quicksum(P_S[s] * m.ZT[s] for s in range(S)) <= a_Var)

    # CVaR constraints (Rockafellar-Uryasev linearization)
    a_CVaR = data["a_CVaR"]
    CVaR_limit = data["CVaR_limit"]
    m.CVaR_u = pyo.Constraint(
        m.IS, rule=lambda m, s: m.u_var[s] >= m.p_shed[s] - m.eta_var)
    m.CVaR = pyo.Constraint(
        expr=m.eta_var
        + (1.0 / (1 - a_CVaR)) * pyo.quicksum(P_S[s] * m.u_var[s]
                                              for s in range(S))
        <= CVaR_limit)

    # ================================================================
    # Part 4 — Con_RR: scenario coupling constraints (based on V_s)
    # ================================================================

    # 4.4 Identify the lines outaged in each scenario
    L_s_number = {}
    for s in range(S):
        L_s_number[s] = np.ones(NL, dtype=float)
        for li in range(NL):
            if (1 - V_s[s, C[li, 0]]) * (1 - V_s[s, C[li, 1]]) >= 1:
                L_s_number[s][li] = 0  # both endpoints outaged -> line outaged

    # R2: lower bound on load shedding (unrestored load in the outaged area)
    def rule_R2(m, s):
        outage_nodes = [n for n in range(N) if V_s[s, n] == 0]
        if len(outage_nodes) == 0:
            return pyo.Constraint.Skip
        return m.p_shed[s] >= pyo.quicksum(
            p_D_mat[t, n] - m.p_load[s, t, n]
            for t in range(T_R) for n in outage_nodes)

    m.R2 = pyo.Constraint(m.IS, rule=rule_R2)

    # Zero out the buses and lines located in the healthy area
    def rule_EnV_off(m, s, t, j):
        if V_s[s, j] == 1:
            return m.En_V[s, t, j] == 0
        return pyo.Constraint.Skip

    m.R_EnV_off = pyo.Constraint(m.IS, m.ITR, m.IB, rule=rule_EnV_off)

    def rule_EnL_off(m, s, t, li):
        if L_s_number[s][li] == 1:
            return m.En_L[s, t, li] == 0
        return pyo.Constraint.Skip

    m.R_EnL_off = pyo.Constraint(m.IS, m.ITR, m.IL, rule=rule_EnL_off)

    # ================================================================
    # Part 5 — Objective
    # ================================================================

    shed_penalty = pyo.quicksum(100 * P_S[s] * m.p_shed[s] for s in range(S))
    m.OBJ = pyo.Objective(expr=C_V + C_OM + C_Inv + shed_penalty,
                          sense=pyo.minimize)

    # ---- Return variable references ----
    var["C_Inv"] = C_Inv
    var["C_OM"] = C_OM
    var["C_V"] = C_V
    var["shed_penalty"] = shed_penalty

    return m, var
