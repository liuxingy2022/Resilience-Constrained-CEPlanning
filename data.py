"""
data.py — System base data and parameter configuration
Corresponds to Chapters 1-2 of the original MATLAB program
(system base data + topology / area partitioning).

All data is returned as a single dict by get_system_data().
"""

import numpy as np


def get_system_data():
    """Load and return all system data and parameters.

    Returns
    -------
    data : dict
        Dict holding all system parameters; keys follow the original
        MATLAB variable names.
    """
    data = {}

    # ================================================================
    # 1. IEEE 39-bus system data
    # ================================================================

    # 1.1 Bus data
    # Cols: bus_i | type | Pd(MW) | Qd(MVAr) | Gs | Bs | area | Vm | Va | baseKV | zone | Vmax | Vmin
    data["Data_bus"] = np.array([
        [  1,   1,   97.6,   44.2,  0,  0,  2,  1.0393836,  -13.536602,  345,  1,  1.06,  0.94],
        [  2,   1,    0,      0,     0,  0,  2,  1.0484941,   -9.7852666, 345,  1,  1.06,  0.94],
        [  3,   1,  322,      2.4,   0,  0,  2,  1.0307077,  -12.276384,  345,  1,  1.06,  0.94],
        [  4,   1,  500,    184,     0,  0,  1,  1.00446,    -12.626734,  345,  1,  1.06,  0.94],
        [  5,   1,    0,      0,     0,  0,  1,  1.0060063,  -11.192339,  345,  1,  1.06,  0.94],
        [  6,   1,    0,      0,     0,  0,  1,  1.0082256,  -10.40833,   345,  1,  1.06,  0.94],
        [  7,   1,  233.8,   84,     0,  0,  1,  0.99839728, -12.755626,  345,  1,  1.06,  0.94],
        [  8,   1,  522,    176.6,   0,  0,  1,  0.99787232, -13.335844,  345,  1,  1.06,  0.94],
        [  9,   1,    6.5,  -66.6,   0,  0,  1,  1.038332,   -14.178442,  345,  1,  1.06,  0.94],
        [ 10,   1,    0,      0,     0,  0,  1,  1.0178431,   -8.170875,  345,  1,  1.06,  0.94],
        [ 11,   1,    0,      0,     0,  0,  1,  1.0133858,   -8.9369663, 345,  1,  1.06,  0.94],
        [ 12,   1,    8.53,  88,     0,  0,  1,  1.000815,    -8.9988236, 345,  1,  1.06,  0.94],
        [ 13,   1,    0,      0,     0,  0,  1,  1.014923,    -8.9299272, 345,  1,  1.06,  0.94],
        [ 14,   1,    0,      0,     0,  0,  1,  1.012319,   -10.715295,  345,  1,  1.06,  0.94],
        [ 15,   1,  320,    153,     0,  0,  3,  1.0161854,  -11.345399,  345,  1,  1.06,  0.94],
        [ 16,   1,  329,     32.3,   0,  0,  3,  1.0325203,  -10.033348,  345,  1,  1.06,  0.94],
        [ 17,   1,    0,      0,     0,  0,  2,  1.0342365,  -11.116436,  345,  1,  1.06,  0.94],
        [ 18,   1,  158,     30,     0,  0,  2,  1.0315726,  -11.986168,  345,  1,  1.06,  0.94],
        [ 19,   1,    0,      0,     0,  0,  3,  1.0501068,   -5.4100729, 345,  1,  1.06,  0.94],
        [ 20,   1,  680,    103,     0,  0,  3,  0.99101054,  -6.8211783, 345,  1,  1.06,  0.94],
        [ 21,   1,  274,    115,     0,  0,  3,  1.0323192,   -7.6287461, 345,  1,  1.06,  0.94],
        [ 22,   1,    0,      0,     0,  0,  3,  1.0501427,   -3.1831199, 345,  1,  1.06,  0.94],
        [ 23,   1,  247.5,   84.6,   0,  0,  3,  1.0451451,   -3.3812763, 345,  1,  1.06,  0.94],
        [ 24,   1,  308.6,  -92.2,   0,  0,  3,  1.038001,    -9.9137585, 345,  1,  1.06,  0.94],
        [ 25,   1,  224,     47.2,   0,  0,  2,  1.0576827,   -8.3692354, 345,  1,  1.06,  0.94],
        [ 26,   1,  139,     17,     0,  0,  2,  1.0525613,   -9.4387696, 345,  1,  1.06,  0.94],
        [ 27,   1,  281,     75.5,   0,  0,  2,  1.0383449,  -11.362152,  345,  1,  1.06,  0.94],
        [ 28,   1,  206,     27.6,   0,  0,  3,  1.0503737,   -5.9283592, 345,  1,  1.06,  0.94],
        [ 29,   1,  283.5,   26.9,   0,  0,  3,  1.0501149,   -3.1698741, 345,  1,  1.06,  0.94],
        [ 30,   2,    0,      0,     0,  0,  2,  1.0499,      -7.3704746, 345,  1,  1.06,  0.94],
        [ 31,   3,    9.2,    4.6,   0,  0,  1,  0.982,        0,         345,  1,  1.06,  0.94],
        [ 32,   2,    0,      0,     0,  0,  1,  0.9841,      -0.1884374, 345,  1,  1.06,  0.94],
        [ 33,   2,    0,      0,     0,  0,  3,  0.9972,      -0.19317445,345,  1,  1.06,  0.94],
        [ 34,   2,    0,      0,     0,  0,  3,  1.0123,      -1.631119,  345,  1,  1.06,  0.94],
        [ 35,   2,    0,      0,     0,  0,  3,  1.0494,       1.7765069, 345,  1,  1.06,  0.94],
        [ 36,   2,    0,      0,     0,  0,  3,  1.0636,       4.4684374, 345,  1,  1.06,  0.94],
        [ 37,   2,    0,      0,     0,  0,  2,  1.0275,      -1.5828988, 345,  1,  1.06,  0.94],
        [ 38,   2,    0,      0,     0,  0,  3,  1.0265,       3.8928177, 345,  1,  1.06,  0.94],
        [ 39,   2, 1104,    250,     0,  0,  1,  1.03,       -14.535256,  345,  1,  1.06,  0.94],
    ])

    # 1.2 Generator data
    # Cols: bus | Pg | Qg | Qmax | Qmin | Vg | mBase | status | Pmax | Pmin | ...
    data["Data_gen"] = np.array([
        [30,  250,     161.762, 400,  -50,   1.0499, 100, 1,  1050, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [31,  677.871, 221.574, 300, -100,   0.982,  100, 1,   600, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [32,  650,     206.965, 300,  -50,   0.9841, 100, 1,   750, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [33,  632,     108.293, 250,  -50,   0.9972, 100, 1,   600, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [34,  508,     166.688, 167,  -50,   1.0123, 100, 1,   600, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [35,  650,     210.661, 300, -100,   1.0494, 100, 1,   600, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [36,  300,     100.165, 120,  -50,   1.0636, 100, 1,   300, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [37,  500,      -1.36945,250, -50,   1.0275, 100, 1,   500, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [38,  830,      21.7327,300, -150,   1.0265, 100, 1,   865, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [39, 1000,      78.4674,300, -100,   1.03,   100, 1,   900, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [36,    0,       0,     120,  -50,   1.0636, 100, 1,   300, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ])

    data["Data_gentype"] = np.array([0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1])  # 0=conventional, 1=renewable

    data["Data_gencost"] = np.array([
        [2, 0, 0, 3, 0.01, 0.3, 0.2],
        [2, 0, 0, 3, 0.01, 0.3, 0.2],
        [2, 0, 0, 3, 0.01, 0.3, 0.2],
        [2, 0, 0, 3, 0.01, 0.3, 0.2],
        [2, 0, 0, 3, 0.01, 0.3, 0.2],
        [2, 0, 0, 3, 0.01, 0.3, 0.2],
        [2, 0, 0, 3, 0.01, 0.3, 0.2],
        [2, 0, 0, 3, 0,    0,   0  ],
        [2, 0, 0, 3, 0.01, 0.3, 0.2],
        [2, 0, 0, 3, 0.01, 0.3, 0.2],
        [2, 0, 0, 3, 0,    0,   0  ],
    ])

    # 1.3 Existing installed capacity per bus and type
    # (row 1 = bus number, rows 2-7 = types F1-F4/W/R)
    # F1=black-start 150MW, F2=black-start 300MW, F3=300MW, F4=600MW, W=wind, R=PV
    data["Date_gen_capa"] = np.array([
        [30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
        [600,600,600,600,600,600,  0,  0,600,600],
        [300,  0,  0,  0,  0,  0,300,  0,  0,300],
        [  0,  0,  0,  0,  0,  0,  0,  0,300,  0],
        [150,  0,150,  0,  0,  0,  0,  0,  0,150],
        [  0,  0,  0,  0,  0,  0,  0,500,  0,  0],
        [  0,  0,  0,  0,  0,  0,300,  0,  0,  0],
    ])

    # Generator type flag per bus (row 1 = bus number, rows 2-6 = type id of each slot)
    data["Date_gen_type"] = np.array([
        [30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
        [ 4,  4,  4,  4,  4,  4,  3,  5,  4,  4],
        [ 3,  0,  1,  0,  0,  0,  6,  0,  2,  3],
        [ 1,  0,  0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    ])

    # 1.4 Branch data
    # Cols: fbus | tbus | r | x | b | rateA | rateB | rateC | ratio | angle | status | angmin | angmax
    data["Data_branch"] = np.array([
        [ 1,  2, 0.0035, 0.0411, 0.6987,  600,  600,  600, 0,     0, 1, -360, 360],
        [ 1, 39, 0.001,  0.025,  0.75,   1000, 1000, 1000, 0,     0, 1, -360, 360],
        [ 2,  3, 0.0013, 0.0151, 0.2572,  500,  500,  500, 0,     0, 1, -360, 360],
        [ 2, 25, 0.007,  0.0086, 0.146,   500,  500,  500, 0,     0, 1, -360, 360],
        [ 2, 30, 0,      0.0181, 0,        900,  900, 2500, 1.025, 0, 1, -360, 360],
        [ 3,  4, 0.0013, 0.0213, 0.2214,  500,  500,  500, 0,     0, 1, -360, 360],
        [ 3, 18, 0.0011, 0.0133, 0.2138,  500,  500,  500, 0,     0, 1, -360, 360],
        [ 4,  5, 0.0008, 0.0128, 0.1342,  600,  600,  600, 0,     0, 1, -360, 360],
        [ 4, 14, 0.0008, 0.0129, 0.1382,  500,  500,  500, 0,     0, 1, -360, 360],
        [ 5,  6, 0.0002, 0.0026, 0.0434, 1200, 1200, 1200, 0,     0, 1, -360, 360],
        [ 5,  8, 0.0008, 0.0112, 0.1476,  900,  900,  900, 0,     0, 1, -360, 360],
        [ 6,  7, 0.0006, 0.0092, 0.113,   900,  900,  900, 0,     0, 1, -360, 360],
        [ 6, 11, 0.0007, 0.0082, 0.1389,  480,  480,  480, 0,     0, 1, -360, 360],
        [ 6, 31, 0,      0.025,  0,       1800, 1800, 1800, 1.07,  0, 1, -360, 360],
        [ 7,  8, 0.0004, 0.0046, 0.078,   900,  900,  900, 0,     0, 1, -360, 360],
        [ 8,  9, 0.0023, 0.0363, 0.3804,  900,  900,  900, 0,     0, 1, -360, 360],
        [ 9, 39, 0.001,  0.025,  1.2,     900,  900,  900, 0,     0, 1, -360, 360],
        [10, 11, 0.0004, 0.0043, 0.0729,  600,  600,  600, 0,     0, 1, -360, 360],
        [10, 13, 0.0004, 0.0043, 0.0729,  600,  600,  600, 0,     0, 1, -360, 360],
        [10, 32, 0,      0.02,   0,        900,  900, 2500, 1.07,  0, 1, -360, 360],
        [12, 11, 0.0016, 0.0435, 0,        500,  500,  500, 1.006, 0, 1, -360, 360],
        [12, 13, 0.0016, 0.0435, 0,        500,  500,  500, 1.006, 0, 1, -360, 360],
        [13, 14, 0.0009, 0.0101, 0.1723,  600,  600,  600, 0,     0, 1, -360, 360],
        [14, 15, 0.0018, 0.0217, 0.366,   600,  600,  600, 0,     0, 1, -360, 360],
        [15, 16, 0.0009, 0.0094, 0.171,   600,  600,  600, 0,     0, 1, -360, 360],
        [16, 17, 0.0007, 0.0089, 0.1342,  600,  600,  600, 0,     0, 1, -360, 360],
        [16, 19, 0.0016, 0.0195, 0.304,   600,  600, 2500, 0,     0, 1, -360, 360],
        [16, 21, 0.0008, 0.0135, 0.2548,  600,  600,  600, 0,     0, 1, -360, 360],
        [16, 24, 0.0003, 0.0059, 0.068,   600,  600,  600, 0,     0, 1, -360, 360],
        [17, 18, 0.0007, 0.0082, 0.1319,  600,  600,  600, 0,     0, 1, -360, 360],
        [17, 27, 0.0013, 0.0173, 0.3216,  600,  600,  600, 0,     0, 1, -360, 360],
        [19, 20, 0.0007, 0.0138, 0,        900,  900, 2500, 1.06,  0, 1, -360, 360],
        [19, 33, 0.0007, 0.0142, 0,        900,  900, 2500, 1.07,  0, 1, -360, 360],
        [20, 34, 0.0009, 0.018,  0,        900,  900, 2500, 1.009, 0, 1, -360, 360],
        [21, 22, 0.0008, 0.014,  0.2565,  900,  900,  900, 0,     0, 1, -360, 360],
        [22, 23, 0.0006, 0.0096, 0.1846,  600,  600,  600, 0,     0, 1, -360, 360],
        [22, 35, 0,      0.0143, 0,        900,  900, 2500, 1.025, 0, 1, -360, 360],
        [23, 24, 0.0022, 0.035,  0.361,   600,  600,  600, 0,     0, 1, -360, 360],
        [23, 36, 0.0005, 0.0272, 0,        900,  900, 2500, 1,     0, 1, -360, 360],
        [25, 26, 0.0032, 0.0323, 0.531,   600,  600,  600, 0,     0, 1, -360, 360],
        [25, 37, 0.0006, 0.0232, 0,        900,  900, 2500, 1.025, 0, 1, -360, 360],
        [26, 27, 0.0014, 0.0147, 0.2396,  600,  600,  600, 0,     0, 1, -360, 360],
        [26, 28, 0.0043, 0.0474, 0.7802,  600,  600,  600, 0,     0, 1, -360, 360],
        [26, 29, 0.0057, 0.0625, 1.029,   600,  600,  600, 0,     0, 1, -360, 360],
        [28, 29, 0.0014, 0.0151, 0.249,   600,  600,  600, 0,     0, 1, -360, 360],
        [29, 38, 0.0008, 0.0156, 0,       1200, 1200, 2500, 1.025, 0, 1, -360, 360],
    ])

    # ================================================================
    # 2. System topology and area partitioning
    # ================================================================

    N = 39       # number of buses
    N_a = 3      # number of areas
    N_F = 4      # number of thermal unit types
    N_ESS = 2    # number of storage types (economic planning dimension)

    data["N"] = N
    data["N_a"] = N_a
    data["N_F"] = N_F
    data["N_ESS"] = N_ESS

    # Buses contained in each area (Python: 0-indexed)
    BusArea = [
        np.array([3,4,5,6,7,8,9,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,31,33,34,35,36,37,38,39]) - 1,
        np.array([10, 11, 32]) - 1,
        np.array([1, 2, 30]) - 1,
    ]
    data["BusArea"] = BusArea

    # Branch connection matrix (46x2, 0-indexed)
    C = data["Data_branch"][:, :2].astype(int) - 1
    data["C"] = C

    # Area adjacency matrix
    adj = np.array([[1, 1, 1],
                     [1, 1, 0],
                     [1, 0, 1]], dtype=float)
    data["adj"] = adj
    data["L_down"] = -500 * adj  # tie-line lower limit
    data["L_up"] = 500 * adj    # tie-line upper limit

    # ================================================================
    # 3. Economic planning parameters
    # ================================================================

    # 3.1 Investment cost ($/kW)
    data["c_Inv_F"] = 600 * np.ones((N_a, N_F))
    data["c_Inv_W"] = 1000 * np.ones((N_a, 1))
    data["c_Inv_R"] = 600 * np.ones((N_a, 1))
    # Storage investment cost: 15% premium for grid-forming, 800 base for grid-following
    data["c_Inv_ESS"] = np.ones((N_a, 1)) * np.array([[800 * 1.15, 800]])

    # 3.2 O&M cost ($/kW/year)
    data["c_OM_F"] = 30 * np.ones((N_a, N_F))
    data["c_OM_W"] = 30 * np.ones((N_a, 1))
    data["c_OM_R"] = 20 * np.ones((N_a, 1))
    data["c_OM_ESS"] = 40 * np.ones((N_a, N_ESS))

    # 3.3 Existing installed capacity (aggregated by area)
    I_FWP0 = np.zeros((N_a, N_F + 2))
    Date_gen_type = data["Date_gen_type"]
    Date_gen_capa = data["Date_gen_capa"]
    for i in range(N_a):
        for j in range(N_F + 2):
            for v in range(len(BusArea[i])):
                bus = BusArea[i][v] + 1  # back to 1-indexed to match the data
                idx = np.where(Date_gen_type[0, :] == bus)[0]
                if len(idx) > 0:
                    I_FWP0[i, j] += np.sum(Date_gen_capa[j + 1, idx])
    data["I_F0"] = I_FWP0[:, :N_F]
    data["I_W0"] = I_FWP0[:, N_F].reshape(-1, 1)
    data["I_R0"] = I_FWP0[:, N_F + 1].reshape(-1, 1)

    # 3.4 Operating parameters
    T = 24
    data["T"] = T
    # Fuel cost ($/kWh): 300 g/kWh x 40 $/ton = 0.012 $/kWh = 12 $/MWh
    # Original program: 300/1000000 * 40 = 0.012 ($/kWh) -> broadcast over an N_a x N_F ones array
    data["c_opera_F"] = 300 / 1000000 * 40 * np.ones((N_a, N_F))
    # Start-up/shut-down cost ($/MW): 150 $/MW -> /1000 to normalize the unit
    data["c_SD_F"] = 150 * np.ones((N_a, N_F)) / 1000

    # 3.5 Area load
    P_D = np.zeros((T, N_a))
    P_D[:, 0] = np.sum(data["Data_bus"][BusArea[0], 2])
    P_D[:, 1] = np.sum(data["Data_bus"][BusArea[1], 2])
    P_D[:, 2] = np.sum(data["Data_bus"][BusArea[2], 2])
    data["P_D"] = P_D

    # 3.6 Storage economic model parameters
    T_ESS = 4  # charge/discharge duration (h)
    data["T_ESS"] = T_ESS
    data["eta_ch"] = 0.95
    data["eta_dis"] = 0.95
    data["SOC_min_ratio"] = 0.10
    data["SOC_max_ratio"] = 0.90
    data["SOC_ini_ratio"] = 0.50

    # ================================================================
    # 4. Restoration resilience planning parameters
    # ================================================================

    N_Z = 2      # max number of thermal/wind/PV units per bus
    N_Z_ESS = 1  # max number of storage units per bus
    S = 5       # number of extreme outage scenarios
    T_R = 6      # restoration horizon (number of time steps)
    p_Line_max = 1000  # line power limit (MW)

    data["N_Z"] = N_Z
    data["N_Z_ESS"] = N_Z_ESS
    data["S"] = S
    data["T_R"] = T_R
    data["p_Line_max"] = p_Line_max

    # 4.1 Storage device-level parameters
    N_ESS_R = 2
    p_ESS_unit_max = np.array([50, 100])      # rated power per unit (MW)
    e_ESS_unit_max = T_ESS * p_ESS_unit_max    # rated energy per unit (MWh) = [200, 400]
    ESS_gridforming = np.array([1, 0])          # 1=grid-forming (can act as a black-start source), 0=grid-following

    data["N_ESS_R"] = N_ESS_R
    data["p_ESS_unit_max"] = p_ESS_unit_max
    data["e_ESS_unit_max"] = e_ESS_unit_max
    data["ESS_gridforming"] = ESS_gridforming

    # Storage parameters for the restoration scenarios
    data["eta_ch_R"] = 0.95
    data["eta_dis_R"] = 0.95
    data["SOC_R_min_ratio"] = 0.10
    data["SOC_R_max_ratio"] = 0.90
    data["SOC_R_ini_ratio"] = 0.80  # pre-charged to 80% before the event

    # 4.2 Per-unit capacity and ramp parameters
    p_F_max = np.array([150, 300, 300, 600])  # max output per thermal unit (MW)
    p_W_max = 500                               # per wind unit
    p_R_max = 300                               # per PV unit
    Ramp = np.array([75, 150, 100, 200])        # ramp rate (MW per time step)
    TCR = np.array([0, 0, 1, 1])                # cold-start time (time steps)
    PCR = np.array([0, 0, 30, 30])              # cranking power (MW)

    data["p_F_max"] = p_F_max
    data["p_W_max"] = p_W_max
    data["p_R_max"] = p_R_max
    data["Ramp"] = Ramp
    data["TCR"] = TCR
    data["PCR"] = PCR

    # ---- Normal-operation ramp rates, per unit of ONLINE capacity ----
    # Used by eq. (18) in the economic planning part:
    #     -rho_down_i * dt * Pbar^F_{i,k,t} <= P^F_{i,k,t} - P^F_{i,k,t-1}
    #                                       <= rho_up_i * dt * Pbar^F_{i,k,t}
    # rho_up[i] / rho_down[i] = upward / downward ramp rate of a type-i thermal
    # unit during normal operation, expressed per unit of its online capacity.
    # Derived from the per-unit ramp capability already used by R6 so that the
    # economic and the restoration ramp limits stay consistent:
    #     rho_i = Ramp[i] / p_F_max[i] = [0.5, 0.5, 1/3, 1/3]   (1/h)
    # Change these two lines if the paper prescribes different values.
    data["rho_up"] = Ramp / p_F_max
    data["rho_down"] = Ramp / p_F_max
    data["DeltaT"] = 1.0  # time-step length (h)

    # 4.3 Scenario probabilities
    P_S = np.ones(S) / S
    data["P_S"] = P_S

    # 4.4 Existing deployment matrices Dep_F_0, Dep_W_0, Dep_R_0 (N_Z x N)
    gen_nodes = Date_gen_type[0, :] - 1  # 0-indexed
    Dep_F_0 = {}
    Dep_W_0 = np.zeros((N_Z, N))
    Dep_R_0 = np.zeros((N_Z, N))

    # Existing thermal deployment: mapped from each row of Date_gen_type
    Dep_F_0[0] = np.zeros((N_Z, N))  # F1: row with type id 3 (Date_gen_type row 3 == 1)
    Dep_F_0[1] = np.zeros((N_Z, N))  # F2: row with type id 2 (Date_gen_type row 4)
    Dep_F_0[2] = np.zeros((N_Z, N))  # F3: all rows with type id 3
    Dep_F_0[3] = np.zeros((N_Z, N))  # F4: all rows with type id 4

    # F1 black-start 150MW: Date_gen_type row=2 (index=1) has values [3,0,1,0,0,0,6,0,2,3]
    # F1=type 1 -> where Date_gen_type[2,:] == 1
    Dep_F_0[0][0, gen_nodes] = np.array([1, 0, 1, 0, 0, 0, 0, 0, 0, 1])   # from line 425
    # F2 black-start 300MW: type 2 -> Date_gen_type[4,:]  # remapped below
    # Actually, from lines 425-430 of the MATLAB source:
    # Dep_F_0{1,1}(1, Date_gen_type(1,:)) = [1 0 1 0 0 0 0 0 0 1]; % F1
    # Dep_F_0{1,2}(1, Date_gen_type(1,:)) = [0 0 0 0 0 0 0 0 1 0]; % F2
    # Dep_F_0{1,3}(1, Date_gen_type(1,:)) = [1 0 0 0 0 0 1 0 0 1]; % F3
    # Dep_F_0{1,4}(1, Date_gen_type(1,:)) = [1 1 1 1 1 1 0 0 1 1]; % F4

    # These are mapped onto Date_gen_type(1,:) which is the bus numbers [30,31,32,33,34,35,36,37,38,39]
    # After -1: [29,30,31,32,33,34,35,36,37,38]
    Dep_F_0[1][0, gen_nodes] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 0])
    Dep_F_0[2][0, gen_nodes] = np.array([1, 0, 0, 0, 0, 0, 1, 0, 0, 1])
    Dep_F_0[3][0, gen_nodes] = np.array([1, 1, 1, 1, 1, 1, 0, 0, 1, 1])

    Dep_W_0[0, gen_nodes] = np.array([0, 0, 0, 0, 0, 0, 0, 1, 0, 0])
    Dep_R_0[0, gen_nodes] = np.array([0, 0, 0, 0, 0, 0, 1, 0, 0, 0])

    data["Dep_F_0"] = Dep_F_0
    data["Dep_W_0"] = Dep_W_0
    data["Dep_R_0"] = Dep_R_0

    # 4.5 Nodal active load matrix (T_R x N)
    p_load_basis = data["Data_bus"][:, 2]  # Pd
    data["p_D_mat"] = np.tile(p_load_basis, (T_R, 1))

    # 4.6 DC power flow parameters
    S_base = 100  # MVA
    x_values = data["Data_branch"][:, 3]   # reactance x (p.u.)
    b_line = S_base / x_values              # susceptance (MW/rad)
    theta_max = np.pi / 3                   # angle limit (+/-60 deg)
    M_dc = b_line * 2 * theta_max + p_Line_max  # per-line Big-M
    bus_ref = 31 - 1                        # reference bus (0-indexed, originally Bus 31)

    data["S_base"] = S_base
    data["b_line"] = b_line
    data["theta_max"] = theta_max
    data["M_dc"] = M_dc
    data["bus_ref"] = bus_ref

    # ================================================================
    # 5. VaR + CVaR risk constraint parameters
    # ================================================================

    data["Var"] = 2000              # VaR threshold (MW per time step)
    data["a_Var"] = 0.15            # VaR confidence level
    data["a_CVaR"] = 0.15           # CVaR confidence level
    data["CVaR_limit"] = 4000       # CVaR upper limit (MW per time step)
    data["M_big"] = 1e4             # big-M constant
    data["M_big_var"] = 999999      # big-M used in the VaR constraints

    # ================================================================
    # 6. Outage scenario matrix V_s (20x39) -- fixed scenarios, hard-coded
    #    V_s[s, j] = 1 -> bus j is healthy;  V_s[s, j] = 0 -> bus j is outaged
    #    Each scenario mimics a cascading outage in a different area.
    #    Note: these scenarios are GIVEN data. The program performs no
    #          cascading-failure simulation and generates no scenarios
    #          iteratively -- V_s is read once at model build time, and a
    #          single solve yields the result. Only the first S rows are used.
    # ================================================================
    V_s = np.ones((20, N), dtype=int)
    # Scenario 0: buses 15,16,17,18 outaged
    V_s[0, [14,15,16,17]] = 0
    # Scenario 1: buses 4,5,6,7 outaged
    V_s[1, [3,4,5,6]] = 0
    # Scenario 2: buses 20,21,22,23,24 outaged
    V_s[2, [19,20,21,22,23]] = 0
    # Scenario 3: buses 25,26,27,28,29 outaged
    V_s[3, [24,25,26,27,28]] = 0
    # Scenario 4: buses 1,2,30 (area 3) outaged
    V_s[4, [0,1,29]] = 0
    # Scenario 5: buses 10,11,32 (area 2) outaged
    V_s[5, [9,10,31]] = 0
    # Scenario 6: buses 31,39 outaged
    V_s[6, [30,38]] = 0
    # Scenario 7: buses 8,9,12,13 outaged
    V_s[7, [7,8,11,12]] = 0
    # Scenario 8: buses 3,17,18 outaged
    V_s[8, [2,16,17]] = 0
    # Scenario 9: buses 14,15,16,19,33 outaged
    V_s[9, [13,14,15,18,32]] = 0
    # Scenario 10: buses 21,22,35 outaged
    V_s[10, [20,21,34]] = 0
    # Scenario 11: buses 23,24,36 outaged
    V_s[11, [22,23,35]] = 0
    # Scenario 12: buses 26,28,29,38 outaged
    V_s[12, [25,27,28,37]] = 0
    # Scenario 13: buses 2,25,37 outaged
    V_s[13, [1,24,36]] = 0
    # Scenario 14: buses 19,20,34 outaged
    V_s[14, [18,19,33]] = 0
    # Scenario 15: large-scale outage -- northern area 1 (buses 4-14)
    V_s[15, [3,4,5,6,7,8,11,12,13]] = 0
    # Scenario 16: medium-scale -- southern area 1 (buses 15-18, 21-24)
    V_s[16, [14,15,16,17,20,21,22,23]] = 0
    # Scenario 17: medium-scale -- eastern area 1 (buses 25-29, 38)
    V_s[17, [24,25,26,27,28,37]] = 0
    # Scenario 18: mixed areas -- buses 1,2,3,30,39 outaged
    V_s[18, [0,1,2,29,38]] = 0
    # Scenario 19: mixed areas -- buses 10,11,12,13,32 outaged
    V_s[19, [9,10,11,12,31]] = 0
    data["V_s"] = V_s[:S]

    # ================================================================
    # 7. Solver parameters (Pyomo version: solver-agnostic)
    #    - the solver is auto-selected by get_solver() in main.py (copt_direct locally)
    #    - RelGap mirrors the original Gurobi MIPGap=0.03 (3% relative gap)
    # ================================================================

    data["solver_params"] = {
        "RelGap": 0.03,        # relative MIP gap (originally MIPGap)
        "TimeLimit": 3600,     # solve time limit (s)
        "Threads": 16,
        "Logging": 1,
    }

    # Original Gurobi option names are kept so they can be reused directly
    # on a machine with Gurobi installed.
    data["gurobi_params"] = {
        "MIPGap": 0.03,
        "MIPFocus": 1,
        "Heuristics": 0.3,
        "TuneTimeLimit": 0,
        "Threads": 16,
    }

    return data


# ================================================================
# Self-check
# ================================================================
if __name__ == "__main__":
    d = get_system_data()
    print("数据加载成功！")
    print(f"  节点数 N = {d['N']}")
    print(f"  区域数 N_a = {d['N_a']}")
    print(f"  火电类型 N_F = {d['N_F']}")
    print(f"  场景数 S = {d['S']}")
    print(f"  恢复时域 T_R = {d['T_R']}")
    print(f"  支路数 NL = {d['C'].shape[0]}")
    print(f"  区域1已有火电容量: {d['I_F0'][0]}")
    print(f"  区域1已有风电容量: {d['I_W0'][0]}")
    print(f"  区域1已有光伏容量: {d['I_R0'][0]}")
