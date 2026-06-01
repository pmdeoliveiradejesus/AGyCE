#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 23 07:59:24 2025

@author: pm.deoliveiradejes  Energy Comunity - Spain 24h
"""
import numpy as np
import numpy_financial as npf
import gurobipy as gp
from   gurobipy import GRB, quicksum
import csv  

# ─────────────────────────────────────────────────────────────────────────────
# 1  CONJUNTO DE HORAS
# ─────────────────────────────────────────────────────────────────────────────
T = range(1, 25)                      # t = 1 … 24


data1 = {
1	    : {'lambda':	0.068746794520548	, 'Plu':	0.135388629090637	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
2	    : {'lambda':	0.064382931506849	, 'Plu':	0.090377249176867	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
3	    : {'lambda':	0.062238410958904	, 'Plu':	0.076343641406536	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
4	    : {'lambda':	0.060464136986301	, 'Plu':	0.075224251241957	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
5	    : {'lambda':	0.060655534246575	, 'Plu':	0.074307578750070	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
6	    : {'lambda':	0.065132136986301	, 'Plu':	0.073105608680250	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
7	    : {'lambda':	0.073826082191781	, 'Plu':	0.073406190057000	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.047492750000000	},
8	    : {'lambda':	0.076148794520548	, 'Plu':	0.085516408757498	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.200034333333333	},
9	    : {'lambda':	0.069382712328767	, 'Plu':	0.883664344082149	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.371942916666667	},
10	    : {'lambda':	0.056760082191781	, 'Plu':	1.000000000000000	 , 'psi': 	0.0319883482993510	, 'Ppvu': 	0.512186250000000	},
11	    : {'lambda':	0.046949369863014	, 'Plu':	0.967245871300936	 , 'psi': 	0.0221906474349675	, 'Ppvu': 	0.605126833333333	},
12	    : {'lambda':	0.041846739726027	, 'Plu':	0.966410238486499	 , 'psi': 	0.0221906474349675	, 'Ppvu': 	0.645309833333333	},
13	    : {'lambda':	0.039593726027397	, 'Plu':	0.122847383567665	 , 'psi': 	0.0221906474349675	, 'Ppvu': 	0.627257666666667	},
14	    : {'lambda':	0.037885123287671	, 'Plu':	0.892179315688642	 , 'psi': 	0.0221906474349675	, 'Ppvu': 	0.568799916666667	},
15	    : {'lambda':	0.036840931506849	, 'Plu':	0.968865480059381	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.473205250000000	},
16	    : {'lambda':	0.038253698630137	, 'Plu':	0.959187873431187	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.337161416666667	},
17	    : {'lambda':	0.046423205479452	, 'Plu':	0.947290206165413	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.188570083333333	},
18	    : {'lambda':	0.059484767123288	, 'Plu':	0.647289021374806	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.043513583333333	},
19	    : {'lambda':	0.076155178082192	, 'Plu':	0.627968640962237	 , 'psi': 	0.0720344854462120	, 'Ppvu': 	0.000000000000000	},
20	    : {'lambda':	0.090286438356164	, 'Plu':	0.659335616819762	 , 'psi': 	0.0512182441617940	, 'Ppvu': 	0.000000000000000	},
21	    : {'lambda':	0.099023506849315	, 'Plu':	0.581590012689108	 , 'psi': 	0.0512182441617940	, 'Ppvu': 	0.000000000000000	},
22	    : {'lambda':	0.090372109589041	, 'Plu':	0.179217943416770	 , 'psi': 	0.0512182441617940	, 'Ppvu': 	0.000000000000000	},
23	    : {'lambda':	0.081188794520548	, 'Plu':	0.144883067091137	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.000000000000000	},
24	    : {'lambda':	0.074767232876712	, 'Plu':	0.138041019820362	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.000000000000000	},
}

data2 = {
1	    : {'lambda':	0.068746794520548	, 'Plu':	0.530061285794532	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
2	    : {'lambda':	0.064382931506849	, 'Plu':	0.531661233031055	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
3	    : {'lambda':	0.062238410958904	, 'Plu':	0.534176029026283	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
4	    : {'lambda':	0.060464136986301	, 'Plu':	0.553334784117771	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
5	    : {'lambda':	0.060655534246575	, 'Plu':	0.618973516973413	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
6	    : {'lambda':	0.065132136986301	, 'Plu':	0.732698140959379	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.000000000000000	},
7	    : {'lambda':	0.073826082191781	, 'Plu':	0.905410448254070	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.047492750000000	},
8	    : {'lambda':	0.076148794520548	, 'Plu':	0.989775313849690	 , 'psi': 	0.0228205053080510	, 'Ppvu': 	0.200034333333333	},
9	    : {'lambda':	0.069382712328767	, 'Plu':	1.000000000000000	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.371942916666667	},
10	    : {'lambda':	0.056760082191781	, 'Plu':	0.980132084762807	 , 'psi': 	0.0319883482993510	, 'Ppvu': 	0.512186250000000	},
11	    : {'lambda':	0.046949369863014	, 'Plu':	0.957725277555312	 , 'psi': 	0.0221906474349675	, 'Ppvu': 	0.605126833333333	},
12	    : {'lambda':	0.041846739726027	, 'Plu':	0.942323657709171	 , 'psi': 	0.0221906474349675	, 'Ppvu': 	0.645309833333333	},
13	    : {'lambda':	0.039593726027397	, 'Plu':	0.913475812983633	 , 'psi': 	0.0221906474349675	, 'Ppvu': 	0.627257666666667	},
14	    : {'lambda':	0.037885123287671	, 'Plu':	0.889945957227714	 , 'psi': 	0.0221906474349675	, 'Ppvu': 	0.568799916666667	},
15	    : {'lambda':	0.036840931506849	, 'Plu':	0.886750273145298	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.473205250000000	},
16	    : {'lambda':	0.038253698630137	, 'Plu':	0.905656297371664	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.337161416666667	},
17	    : {'lambda':	0.046423205479452	, 'Plu':	0.861890166282270	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.188570083333333	},
18	    : {'lambda':	0.059484767123288	, 'Plu':	0.701714201302491	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.043513583333333	},
19	    : {'lambda':	0.076155178082192	, 'Plu':	0.351262364643030	 , 'psi': 	0.0720344854462120	, 'Ppvu': 	0.000000000000000	},
20	    : {'lambda':	0.090286438356164	, 'Plu':	0.338840454837792	 , 'psi': 	0.0512182441617940	, 'Ppvu': 	0.000000000000000	},
21	    : {'lambda':	0.099023506849315	, 'Plu':	0.317456333765505	 , 'psi': 	0.0512182441617940	, 'Ppvu': 	0.000000000000000	},
22	    : {'lambda':	0.090372109589041	, 'Plu':	0.293644351056787	 , 'psi': 	0.0512182441617940	, 'Ppvu': 	0.000000000000000	},
23	    : {'lambda':	0.081188794520548	, 'Plu':	0.274768244366155	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.000000000000000	},
24	    : {'lambda':	0.074767232876712	, 'Plu':	0.331848323823927	 , 'psi': 	0.0210743713052406	, 'Ppvu': 	0.000000000000000	},
    }



# ─────────────────────────────────────────────────────────────────────────────
# 3  ESCALARES
# ─────────────────────────────────────────────────────────────────────────────
# ── Activos eléctricos
Ppvmax1 = 569.0                       # kWp instalados
Plmax1  = 231.241369863014            # kW pico de carga
SOC01   = 100.0                       # kWh al inicio
C1      = 2000.0                      # kWh (capacidad batería)
eff_c1  = 0.93                        # eficiencia carga
eff_d1  = 0.97                        # eficiencia descarga
R_c1    = 0.20                        # máx C-rate de carga
R_d1    = 0.20                        # máx C-rate de descarga
DoD1    = 0.90
Pmax1   = 600.0                       # límite inverter export/import
Capacity01 = -31713.9
CAPEXpv = 700
CAPEX_BESS = 200
CAPEX_BESS_inverter = 80
crf       = 0.08024258719069
# ── Cargos de capacidad en España (€/kW-año)
kappaP1, kappaP2, kappaP3 = 28.79187, 15.07764,  6.55917
kappaP4, kappaP5, kappaP6 =  5.17209,  1.93281,  0.91609
PbmaxP11, PbmaxP21, PbmaxP31 = 504.43000000,    453.96686700,   404.47000000
PbmaxP41, PbmaxP51, PbmaxP61 = 442.91000000,    338.0551530,    564.30000000
capac_cost1 = (kappaP1*PbmaxP11 + kappaP2*PbmaxP21 + kappaP3*PbmaxP31 +
              kappaP4*PbmaxP41 + kappaP5*PbmaxP51 + kappaP6*PbmaxP61)

# ── Activos eléctricos
Ppvmax2 = 800                       # kWp instalados
Plmax2  = 312.78235978049            # kW pico de carga
SOC02   = 140.0                       # kWh al inicio
C2      = 2800.0                      # kWh (capacidad batería)
eff_c2  = 0.92                        # eficiencia carga
eff_d2  = 0.95                        # eficiencia descarga
R_c2    = 0.30                        # máx C-rate de carga
R_d2    = 0.30                        # máx C-rate de descarga
DoD2    = 0.90
Pmax2   = 650.0                       # límite inverter export/import
Capacity02 = -33786.68
CAPEXpv = 700
CAPEX_BESS = 200
CAPEX_BESS_inverter = 80
crf       = 0.08024258719069
# ── Cargos de capacidad en España (€/kW-año)
kappaP1, kappaP2, kappaP3 = 28.79187, 15.07764,  6.55917
kappaP4, kappaP5, kappaP6 =  5.17209,  1.93281,  0.91609
PbmaxP12, PbmaxP22, PbmaxP32 = 408.15430000, 437.71230000, 494.17200000
PbmaxP42, PbmaxP52, PbmaxP62 = 561.32090000, 379.49780000, 553.88960000
capac_cost2 = (kappaP1*PbmaxP12 + kappaP2*PbmaxP22 + kappaP3*PbmaxP32 +
              kappaP4*PbmaxP42 + kappaP5*PbmaxP52 + kappaP6*PbmaxP62)
varphib=0.00375
varphis= 0.00125
PmaxCDS=  400
CAPEX_I1=830300
CAPEX_I2=1187200


# ── Límites SOC batería
SOC_up1 = ((1-DoD1)/2 + DoD1)*C1
SOC_lo1 = ((1-DoD1)/2)*C1
SOC_up2 = ((1-DoD2)/2 + DoD2)*C2
SOC_lo2 = ((1-DoD2)/2)*C2


m = gp.Model('AGPE_España')

# 4.1 VARIABLES ──────────────────────────────────────────────────────────────
npv = m.addVar(name='npv', lb=-GRB.INFINITY)
npv1 = m.addVar(name='npv1', lb=-GRB.INFINITY)
Benefit1 = m.addVar(name='Benefit1', lb=-GRB.INFINITY)
Base1 = m.addVar(name='Base1', lb=-GRB.INFINITY)
CashFlow1 = m.addVar(name='CashFlow1', lb=-GRB.INFINITY)
Investment1 = m.addVar(name='Investment1', lb=-GRB.INFINITY)
# Batería y red
SOC1 = {t: m.addVar(lb=SOC_lo1, ub=SOC_up1, name=f'SOC[{t}]1') for t in T}
Pd1  = {t: m.addVar(lb=0, name=f'Pd[{t}]1')  for t in T}
Pc1  = {t: m.addVar(lb=0, name=f'Pc[{t}]1')  for t in T}
Pb1  = {t: m.addVar(lb=0, name=f'Pb[{t}]1')  for t in T}
Ps1  = {t: m.addVar(lb=0, name=f'Ps[{t}]1')  for t in T}
w11  = {t: m.addVar(vtype=GRB.BINARY, name=f'w1[{t}]1') for t in T}
w31  = {t: m.addVar(vtype=GRB.BINARY, name=f'w3[{t}]1') for t in T}
npv2 = m.addVar(name='npv2', lb=-GRB.INFINITY)
Benefit2 = m.addVar(name='Benefit2', lb=-GRB.INFINITY)
Base2 = m.addVar(name='Base2', lb=-GRB.INFINITY)
CashFlow2 = m.addVar(name='CashFlow2', lb=-GRB.INFINITY)
Investment2 = m.addVar(name='Investment2', lb=-GRB.INFINITY)
# Batería y red
SOC2 = {t: m.addVar(lb=SOC_lo2, ub=SOC_up2, name=f'SOC[{t}]1') for t in T}
Pd2  = {t: m.addVar(lb=0, name=f'Pd[{t}]2')  for t in T}
Pc2  = {t: m.addVar(lb=0, name=f'Pc[{t}]2')  for t in T}
Pb2  = {t: m.addVar(lb=0, name=f'Pb[{t}]2')  for t in T}
Ps2  = {t: m.addVar(lb=0, name=f'Ps[{t}]2')  for t in T}
w12  = {t: m.addVar(vtype=GRB.BINARY, name=f'w1[{t}]2') for t in T}
w32  = {t: m.addVar(vtype=GRB.BINARY, name=f'w3[{t}]2') for t in T}
v12  = {t: m.addVar(vtype=GRB.BINARY, name=f'v12[{t}]') for t in T}
P12CDS   = {t: m.addVar(lb=0, name=f'P12CDS')  for t in T}
P21CDS   = {t: m.addVar(lb=0, name=f'P21CDS')  for t in T}
epsilon  = {t: m.addVar(lb=0, name=f'epsilon')  for t in T}
IndustryProfit  =  m.addVar(name='IndustryProfit', lb=-GRB.INFINITY)
CW              =  m.addVar(name='CW', lb=-GRB.INFINITY)
EP1            =  m.addVar(name='EP1', lb=-GRB.INFINITY)
EP2           =   m.addVar(name='EP2', lb=-GRB.INFINITY)
E1            =   m.addVar(name='E1', lb=-GRB.INFINITY)
E2            =   m.addVar(name='E2', lb=-GRB.INFINITY)
APA           =   m.addVar(name='APA', lb=-GRB.INFINITY)
I1_Profit     =   m.addVar(name='I1_Profit', lb=-GRB.INFINITY)
I2_Profit     =   m.addVar(name='I2_Profit', lb=-GRB.INFINITY)
AP1           =   m.addVar(name='AP1', lb=-GRB.INFINITY)
AP2           =   m.addVar(name='AP2', lb=-GRB.INFINITY)
delta    =  m.addVar(name='delta', lb=-GRB.INFINITY)


# 4.2 FUNCIÓN DE BENEFICIO ───────────────────────────────────────────────────
m.addConstr(
    Benefit1 ==
        - capac_cost1                                           # €/año (potencia)
        + 365 * (
            quicksum( data1[t]['lambda'] * Ps1[t]
                    - (data1[t]['lambda'] + data1[t]['psi']) * Pb1[t]
                    for t in T )
          ),
    name='Bcalc_1'
)
# 4.3 BALANCE ENERGÉTICO ─────────────────────────────────────────────────────
for t in T:
    m.addConstr(
        Pd1[t] + Pb1[t] + Ppvmax1 * data1[t]['Ppvu'] + P21CDS[t] - P12CDS[t] ==
        Pc1[t] + Ps1[t] + Plmax1 * data1[t]['Plu'],
        name=f'balance[{t}]'
    )
# 4.4 DINÁMICA DEL SOC ───────────────────────────────────────────────────────
for t in T:
    if t == 1:
        m.addConstr(SOC1[t] == SOC01 + Pc1[t]*eff_c1 - Pd1[t]/eff_d1,
                    name=f'SOC_dyn[{t}]')
    else:
        m.addConstr(SOC1[t] == SOC1[t-1] + Pc1[t]*eff_c1 - Pd1[t]/eff_d1,
                    name=f'SOC_dyn[{t}]_1')
SOC1[24].LB = SOC01
SOC1[24].UB = SOC01
# 4.5 BATERÍA: CARGA / DESCARGA EXCLUYENTE ───────────────────────────────────
for t in T:
    m.addConstr(Pc1[t] <= R_c1*C1 * w11[t],        name=f'r_Pc[{t}]_1')
    m.addConstr(Pd1[t] <= R_d1*C1 * (1-w11[t]),    name=f'r_Pd[{t}]_1')
    m.addConstr(Pb1[t] <= Pmax1 * w31[t],         name=f'r_Pb[{t}]_1')
    m.addConstr(Ps1[t] <= Pmax1 * (1-w31[t]),     name=f'r_Ps[{t}]_1')
# 4.6 LÍMITES DE POTENCIA POR BLOQUE ─────────────────────────────────────────
for t in range(1,  8):  m.addConstr(Pb1[t] <= PbmaxP61, name=f'r6_13_PbmaxP6[{t}]_1')
m.addConstr(Pb1[ 9] <= PbmaxP51, name='r14_PbmaxP5_1')
m.addConstr(Pb1[10] <= PbmaxP31, name='r15_PbmaxP3_1')
for t in range(11, 14): m.addConstr(Pb1[t] <= PbmaxP41, name=f'r16_19_PbmaxP4[{t}]_1')
for t in range(15, 18): m.addConstr(Pb1[t] <= PbmaxP51, name=f'r20_23_PbmaxP5[{t}]_1')
m.addConstr(Pb1[19] <= PbmaxP11, name='r24_PbmaxP1_1')
for t in range(20, 22): m.addConstr(Pb1[t] <= PbmaxP21, name=f'r25_27_PbmaxP2[{t}]_1')
for t in range(23, 24): m.addConstr(Pb1[t] <= PbmaxP51, name=f'r28_29_PbmaxP5[{t}]_1')
# 4.9 ANALISIS FINANCIERO
m.addConstr(CashFlow1 == Benefit1-Base1, name='r7_1')
m.addConstr(Investment1 ==    CAPEXpv*Ppvmax1+CAPEX_BESS*C1+CAPEX_BESS_inverter*C1*R_c1, name='r8_1')
m.addConstr(npv1 == CashFlow1/crf-Investment1, name='r9_1')
for t in T:
    m.addConstr(Base1 ==(
            -quicksum((data1[t]['lambda'] + data1[t]['psi']) * Plmax1 * data1[t]['Plu']*365
                    for t in T )+Capacity01
          ), name='r10_1')


# 4.2 FUNCIÓN DE BENEFICIO ───────────────────────────────────────────────────
m.addConstr(
    Benefit2 ==
        - capac_cost2                                           # €/año (potencia)
        + 365 * (
            quicksum( data2[t]['lambda'] * Ps2[t]
                    - (data2[t]['lambda'] + data2[t]['psi']) * Pb2[t]
                    for t in T )
          ),
    name='Bcalc_1'
)
# 4.3 BALANCE ENERGÉTICO ─────────────────────────────────────────────────────
for t in T:
    m.addConstr(
        Pd2[t] + Pb2[t] + Ppvmax2 * data2[t]['Ppvu'] ==
        Pc2[t] + Ps2[t] + Plmax2 * data2[t]['Plu'] + P21CDS[t] - P12CDS[t],
        name=f'balance[{t}]'
    )
# 4.4 DINÁMICA DEL SOC ───────────────────────────────────────────────────────
for t in T:
    if t == 1:
        m.addConstr(SOC2[t] == SOC02 + Pc2[t]*eff_c2 - Pd2[t]/eff_d2,
                    name=f'SOC_dyn[{t}] 2')
    else:
        m.addConstr(SOC2[t] == SOC2[t-1] + Pc2[t]*eff_c2 - Pd2[t]/eff_d2,
                    name=f'SOC_dyn[{t}]_22')
SOC2[24].LB = SOC02
SOC2[24].UB = SOC02
# 4.5 BATERÍA: CARGA / DESCARGA EXCLUYENTE ───────────────────────────────────
for t in T:
    m.addConstr(Pc2[t] <= R_c2*C2 * w12[t],        name=f'r_Pc[{t}]_1')
    m.addConstr(Pd2[t] <= R_d2*C2 * (1-w12[t]),    name=f'r_Pd[{t}]_1')
    m.addConstr(Pb2[t] <= Pmax2 * w32[t],         name=f'r_Pb[{t}]_1')
    m.addConstr(Ps2[t] <= Pmax2 * (1-w32[t]),     name=f'r_Ps[{t}]_1')
# 4.6 LÍMITES DE POTENCIA POR BLOQUE ─────────────────────────────────────────
for t in range(1,  8):  m.addConstr(Pb2[t] <= PbmaxP62, name=f'r6_13_PbmaxP6[{t}]_2')
m.addConstr(Pb2[ 9] <= PbmaxP52, name='r14_PbmaxP5_2')
m.addConstr(Pb2[10] <= PbmaxP32, name='r15_PbmaxP3_2')
for t in range(11, 14): m.addConstr(Pb2[t] <= PbmaxP42, name=f'r16_19_PbmaxP4[{t}]_2')
for t in range(15, 18): m.addConstr(Pb2[t] <= PbmaxP52, name=f'r20_23_PbmaxP5[{t}]_2')
m.addConstr(Pb2[19] <= PbmaxP12, name='r24_PbmaxP1_2')
for t in range(20, 22): m.addConstr(Pb2[t] <= PbmaxP22, name=f'r25_27_PbmaxP2[{t}]_2')
for t in range(23, 24): m.addConstr(Pb2[t] <= PbmaxP52, name=f'r28_29_PbmaxP5[{t}]_2')
# 4.9 ANALISIS FINANCIERO
m.addConstr(CashFlow2 == Benefit2-Base2, name='r7_2')
m.addConstr(Investment2 ==    CAPEXpv*Ppvmax2+CAPEX_BESS*C2+CAPEX_BESS_inverter*C2*R_c2, name='r8_2')
m.addConstr(npv2 == CashFlow2/crf-Investment2, name='r9_2')
for t in T:
    m.addConstr(Base2 ==(
            -quicksum((data2[t]['lambda'] + data2[t]['psi']) * Plmax2 * data2[t]['Plu']*365
                    for t in T )+Capacity02
          ), name='r10_2')
    
    
m.addConstr(IndustryProfit ==  I1_Profit+ I2_Profit) 
m.addConstr(CW ==  EP1+E1+EP2+E2+APA) 
m.addConstr(EP1 == Benefit1)
m.addConstr(EP2 == Benefit2) 
m.addConstr(E1 ==  365*(quicksum( (epsilon[t]-varphis)*P12CDS[t] for t in T )-quicksum( (epsilon[t]+varphib)*P21CDS[t] for t in T )))
m.addConstr(E2 ==  365*(quicksum( (epsilon[t]-varphis)*P21CDS[t] for t in T )-quicksum( (epsilon[t]+varphib)*P12CDS[t] for t in T )))
m.addConstr(APA  ==(2*delta)*PmaxCDS+(365)*(quicksum((varphis+varphib)*(P12CDS[t]+P21CDS[t])for t in T )))     
m.addConstr(I1_Profit == EP1+E1)
m.addConstr(I2_Profit == EP2+E2)
m.addConstr(AP1== EP1+E1)
m.addConstr(AP2== EP2+E2)
m.addConstr(CAPEX_I2*I1_Profit==CAPEX_I1*I2_Profit,name='Bcalc_11')
m.addConstr(delta <= kappaP1)
m.addConstr(delta <= kappaP2)
m.addConstr(delta <= kappaP3)
m.addConstr(delta <= kappaP4)
m.addConstr(delta <= kappaP5)
m.addConstr(delta <= kappaP6)
m.addConstr(delta >= 0)
for t in T: 
    m.addConstr(epsilon[t] <= data2[t]['lambda'] + data2[t]['psi'])
    m.addConstr(epsilon[t] >= data2[t]['lambda'])            
    m.addConstr(P12CDS[t] <= PmaxCDS*v12[t])
    m.addConstr(P21CDS[t] <= PmaxCDS*(1-v12[t]))

m.addConstr(npv==(IndustryProfit-Base1-Base2)/crf-Investment1-Investment2)
    
# 4.8 OBJETIVO
m.setObjective(IndustryProfit, GRB.MAXIMIZE)
# ─────────────────────────────────────────────────────────────────────────────
# 5  OPTIMIZACIÓN
# ─────────────────────────────────────────────────────────────────────────────
m.optimize()
# ─────────────────────────────────────────────────────────────────────────────
# 6  RESULTADOS BÁSICOS
# ─────────────────────────────────────────────────────────────────────────────

if m.status == gp.GRB.OPTIMAL:
    with open('solution_M1_7_E1e.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow(["Hour", "Pb1", "Ps1", "Pc1", "Pd1", "Pb2", "Ps2", "Pc2", "Pd2",
                                                  "SOC1",	"SOC2","epsilon","P12CDS","P21CDS"])
        # Write each hour's data
        for t in T:
            writer.writerow([
                t,
                Pb1[t].X,
                Ps1[t].X,
                Pc1[t].X,
                Pd1[t].X,
                Pb2[t].X,
                Ps2[t].X,
                Pc2[t].X,
                Pd2[t].X,
                SOC1[t].X,
                SOC2[t].X,
  			    epsilon[t].X,	
                P12CDS[t].X,
                P21CDS[t].X
            ])
    print("Solution written to solution_M1_7_E1e.csv")

if m.Status == GRB.OPTIMAL:
    print(f"Delta  : {delta.X:,.2f} €/año")
    print(f"IndustryProfit  : {IndustryProfit.X:,.2f} €/año")
    print(f"NPV  : {npv.X:,.2f} €/año") 
    print(f"NPV1  : {npv1.X:,.2f} €/año")    
    print(f"NPV2  : {npv2.X:,.2f} €/año")
    print(f"Base1  : {Base1.X:,.2f} €/año")    
    print(f"Base2  : {Base2.X:,.2f} €/año")
    print(f"Investment1  : {Investment1.X:,.2f} €/año")    
    print(f"Investment2  : {Investment2.X:,.2f} €/año") 
    print(f"Benefit1  : {Benefit1.X:,.2f} €/año")    
    print(f"Benefit2  : {Benefit2.X:,.2f} €/año") 
    print(f"CashFlow1  : {CashFlow1.X:,.2f} €/año")    
    print(f"CashFlow2  : {CashFlow2.X:,.2f} €/año")    
    print(f"APA  : {APA.X:,.2f} €/año")
    print(f"CW  :  {CW.X:,.2f} €/año")
    print(f"E 1  : {E1.X:,.2f} €/año")
    print(f"E 2  : {E2.X:,.2f} €/año")
    print(f"EP 1  : {EP1.X:,.2f} €/año")
    print(f"EP 2  : {EP2.X:,.2f} €/año")
    print(f"AP 1  : {AP1.X:,.2f} €/año")
    print(f"AP 2  : {AP2.X:,.2f} €/año")
    print(f"IndustryProfit 1  : {I1_Profit.X:,.2f} €/año")
    print(f"IndustryProfit 2  : {I2_Profit.X:,.2f} €/año")
    #for t in T: 
   #     print(f" {Pb1[t].X:,.12f}  ") 
else:
    print("No se alcanzó solución óptima.  Código de estado:", m.Status)


# Basic Financial Analysis INDUSTRY 1 + INDUSTRY 2
Io = Investment1.X + Investment2.X # CAPEX in USD
Rate = 0.05  # Discount rate (5%)
S = IndustryProfit.X-Base1.X-Base2.X  # OPEX
n = 20  # Lifetime in years
# Cash flows
CashFlow = np.ones(n) * S
# Net Present Value (NPV)
NPV = -Io + npf.pv(rate=Rate, nper=n, pmt=-S, fv=0)
# Internal Rate of Return (IRR)
TIR = npf.irr([-Io] + list(CashFlow)) * 100
# Benefit-Cost Ratio
BCratio = npf.pv(rate=Rate, nper=n, pmt=-S, fv=0) / Io
# Define input parameters for NPER calculation
PV = -Io  # Present Value (initial investment)
PMT = S   # Payment per period
rate = Rate
FV = 0  # Future Value

# Calculate the number of periods (NPER)
if rate == 0:
    NPER = PV / PMT
else:
    NPER = np.log((PMT - rate * FV) / (PMT + rate * PV)) / np.log(1 + rate)   
    
if m.Status == GRB.OPTIMAL:
    print(f"Resultados Financieros:")
    print(f"---------------------")
    print(f"Investment: {Io:,.2f} €/año")
    print(f"CashFlow: {S:,.2f} €/año")
    print(f"NPV:      {NPV:,.2f} €")   
    print(f"TIR:      {TIR:,.2f} %")
    print(f"NPER:     {NPER:,.2f} años")
    print(f"B/C Ratio {BCratio:,.2f}")    
    
    
# Optimal solution found (tolerance 1.00e-04)
# Best objective -7.971612439778e+04, best bound -7.971612439778e+04, gap 0.0000%
# Solution written to solution.csv
# Delta  : 0.00 €/año
# IndustryProfit  : -79,716.12 €/año
# NPV  : 782,487.85 €/año
# NPV1  : 447,986.31 €/año
# NPV2  : 357,370.25 €/año
# Base1  : -114,101.65 €/año
# Base2  : -190,292.74 €/año
# Investment1  : 830,300.00 €/año
# Investment2  : 1,187,200.00 €/año
# Benefit1  : -11,528.65 €/año
# Benefit2  : -66,352.43 €/año
# CashFlow1  : 102,573.00 €/año
# CashFlow2  : 123,940.31 €/año
# APA  : 1,835.04 €/año
# CW  :  -77,881.08 €/año
# E 1  : -21,278.44 €/año
# E 2  : 19,443.39 €/año
# EP 1  : -11,528.65 €/año
# EP 2  : -66,352.43 €/año
# AP 1  : -32,807.09 €/año
# AP 2  : -46,909.04 €/año
# IndustryProfit 1  : -32,807.09 €/año
# IndustryProfit 2  : -46,909.04 €/año
# Resultados Financieros:
# ---------------------
# Investment: 2,017,500.00 €/año
# CashFlow: 224,678.27 €/año
# NPV:      782,487.85 €
# TIR:      9.23 %
# NPER:     12.22 años
# B/C Ratio 1.39    