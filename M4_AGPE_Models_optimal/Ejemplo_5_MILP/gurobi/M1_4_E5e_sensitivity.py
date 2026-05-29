#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 28 11:15:26 2026

@author: pm.deoliveiradejes
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de sensibilidad del CAPEX PV sobre KPIs (TIR, PBT, NPV, LCOEgross)
"""
import numpy as np
import numpy_financial as npf
import gurobipy as gp
from gurobipy import GRB, quicksum
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# 1  CONJUNTO DE HORAS
# ─────────────────────────────────────────────────────────────────────────────
T = range(1, 25)                      # t = 1 … 24

# ─────────────────────────────────────────────────────────────────────────────
# 2  TABLA «data»  (precio spot λ, perfil de carga Plu, peaje psi, PV pu)
# ─────────────────────────────────────────────────────────────────────────────
data = {
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

# ─────────────────────────────────────────────────────────────────────────────
# 3  ESCALARES CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────
Ppvmax = 569.0                       # kWp instalados
Plmax  = 231.241369863014            # kW pico de carga
SOC0   = 100.0                       # kWh al inicio
C      = 2000.0                      # kWh (capacidad batería)
eff_c  = 0.93                        # eficiencia carga
eff_d  = 0.97                        # eficiencia descarga
R_c    = 0.20                        # máx C-rate de carga
R_d    = 0.20                        # máx C-rate de descarga
DoD    = 0.90
Pmax   = 600.0                       # límite inverter export/import
Capacity0 = -31713.9
CAPEX_BESS = 200
CAPEX_BESS_inverter = 80
crf       = 0.08024258719069

# Cargos de capacidad
kappaP1, kappaP2, kappaP3 = 28.79187, 15.07764,  6.55917
kappaP4, kappaP5, kappaP6 =  5.17209,  1.93281,  0.91609
PbmaxP1, PbmaxP2, PbmaxP3 = 504.43000000,    453.96686700,   404.47000000
PbmaxP4, PbmaxP5, PbmaxP6 = 442.91000000,    338.0551530,    564.30000000
capac_cost = (kappaP1*PbmaxP1 + kappaP2*PbmaxP2 + kappaP3*PbmaxP3 +
              kappaP4*PbmaxP4 + kappaP5*PbmaxP5 + kappaP6*PbmaxP6)

SOC_up = ((1-DoD)/2 + DoD)*C
SOC_lo = ((1-DoD)/2)*C

# ─────────────────────────────────────────────────────────────────────────────
# 4  DEFINICIÓN DEL RANGO DE SENSIBILIDAD
# ─────────────────────────────────────────────────────────────────────────────
capex_pv_range = np.arange(300, 1001, 25)

# Listas para almacenar las métricas resultantes
list_capex = []
list_tir = []
list_nper = []
list_npv = []
list_lcoe_gross = []

print("Ejecutando análisis de sensibilidad...")
print(f"{'CAPEXpv':<10}{'TIR (%)':<10}{'PBT (Años)':<12}{'NPV (€)':<15}{'LCOE Gross':<12}")
print("-" * 60)

# ─────────────────────────────────────────────────────────────────────────────
# 5  BUCLE DE OPTIMIZACIÓN Y CÁLCULO
# ─────────────────────────────────────────────────────────────────────────────
for cpv in capex_pv_range:
    m = gp.Model('AGPE_España')
    m.Params.OutputFlag = 0  # Silenciar Gurobi para una salida limpia
    
    # VARIABLES
    npv_var = m.addVar(name='npv', lb=-GRB.INFINITY)
    Benefit = m.addVar(name='Benefit', lb=-GRB.INFINITY)
    Base = m.addVar(name='Base', lb=-GRB.INFINITY)
    CashFlow_var = m.addVar(name='CashFlow', lb=-GRB.INFINITY)
    Investment = m.addVar(name='Investment', lb=-GRB.INFINITY)
    
    SOC = {t: m.addVar(lb=SOC_lo, ub=SOC_up, name=f'SOC[{t}]') for t in T}
    Pd  = {t: m.addVar(lb=0, name=f'Pd[{t}]')  for t in T}
    Pc  = {t: m.addVar(lb=0, name=f'Pc[{t}]')  for t in T}
    Pb  = {t: m.addVar(lb=0, name=f'Pb[{t}]')  for t in T}
    Ps  = {t: m.addVar(lb=0, name=f'Ps[{t}]')  for t in T}
    w1  = {t: m.addVar(vtype=GRB.BINARY, name=f'w1[{t}]') for t in T}
    w3  = {t: m.addVar(vtype=GRB.BINARY, name=f'w3[{t}]') for t in T}
    Wl = m.addVar(name='Wl', lb=0)
    Es = m.addVar(name='Es', lb=0)
    Eb = m.addVar(name='Eb', lb=0)
    OPEX = m.addVar(name='OPEX', lb=0)
    
    # CONSTR: FUNCIÓN DE BENEFICIO
    m.addConstr(
        Benefit == - capac_cost + 365 * (
            quicksum(data[t]['lambda'] * Ps[t] - (data[t]['lambda'] + data[t]['psi']) * Pb[t] for t in T)
        ), name='Bcalc'
    )
    
    # CONSTR: BALANCE ENERGÉTICO
    for t in T:
        m.addConstr(
            Pd[t] + Pb[t] + Ppvmax * data[t]['Ppvu'] == Pc[t] + Ps[t] + Plmax * data[t]['Plu'],
            name=f'balance[{t}]'
        )
        
    # CONSTR: DINÁMICA SOC
    for t in T:
        if t == 1:
            m.addConstr(SOC[t] == SOC0 + Pc[t]*eff_c - Pd[t]/eff_d, name=f'SOC_dyn[{t}]')
        else:
            m.addConstr(SOC[t] == SOC[t-1] + Pc[t]*eff_c - Pd[t]/eff_d, name=f'SOC_dyn[{t}]')
    SOC[24].LB = SOC0
    SOC[24].UB = SOC0
    
    # CONSTR: EXCLUSIVIDAD BATERÍA
    for t in T:
        m.addConstr(Pc[t] <= R_c*C * w1[t],        name=f'r_Pc[{t}]')
        m.addConstr(Pd[t] <= R_d*C * (1-w1[t]),    name=f'r_Pd[{t}]')
        m.addConstr(Pb[t] <= Pmax * w3[t],         name=f'r_Pb[{t}]')
        m.addConstr(Ps[t] <= Pmax * (1-w3[t]),     name=f'r_Ps[{t}]')
        
    # CONSTR: LÍMITES POR BLOQUE
    for t in range(1,  8):  m.addConstr(Pb[t] <= PbmaxP6, name=f'r6_13_PbmaxP6[{t}]')
    m.addConstr(Pb[ 9] <= PbmaxP5, name='r14_PbmaxP5')
    m.addConstr(Pb[10] <= PbmaxP3, name='r15_PbmaxP3')
    for t in range(11, 14): m.addConstr(Pb[t] <= PbmaxP4, name=f'r16_19_PbmaxP4[{t}]')
    for t in range(15, 18): m.addConstr(Pb[t] <= PbmaxP5, name=f'r20_23_PbmaxP5[{t}]')
    m.addConstr(Pb[19] <= PbmaxP1, name='r24_PbmaxP1')
    for t in range(20, 22): m.addConstr(Pb[t] <= PbmaxP2, name=f'r25_27_PbmaxP2[{t}]')
    for t in range(23, 24): m.addConstr(Pb[t] <= PbmaxP5, name=f'r28_29_PbmaxP5[{t}]')
    
    # ANALISIS FINANCIERO (Usa la variable local 'cpv' del bucle)
    m.addConstr(CashFlow_var == Benefit - Base, name='r7')
    m.addConstr(Investment == cpv*Ppvmax + CAPEX_BESS*C + CAPEX_BESS_inverter*C*R_c, name='r8')
    m.addConstr(npv_var == CashFlow_var/crf - Investment, name='r9')
    m.addConstr(Wl == 365*sum(Plmax * data[t]['Plu'] for t in T))
    m.addConstr(Es == 365*(quicksum(data[t]['lambda'] * Ps[t] for t in T)))
    m.addConstr(Eb == 365*(quicksum((data[t]['lambda'] + data[t]['psi']) * Pb[t] for t in T)))
    m.addConstr(OPEX == capac_cost + Eb)
    
    for t in T:
        m.addConstr(Base == (
                -quicksum((data[t]['lambda'] + data[t]['psi']) * Plmax * data[t]['Plu']*365 for t in T) + Capacity0
              ), name='r10')
        
    m.setObjective(Benefit, GRB.MAXIMIZE)
    m.optimize()
    
    # Extracción de KPIs financieros si es Óptimo
    if m.Status == GRB.OPTIMAL:
        Io = Investment.X
        Rate = 0.05
        S = CashFlow_var.X
        n = 20
        
        CashFlow_arr = np.ones(n) * S
        NPV_fin = -Io + npf.pv(rate=Rate, nper=n, pmt=-S, fv=0)
        TIR_fin = npf.irr([-Io] + list(CashFlow_arr)) * 100
        
        PV_val = -Io
        PMT_val = S
        
        if Rate == 0:
            NPER_fin = PV_val / PMT_val
        else:
            # Prevención de errores matemáticos si el argumento del log es negativo o cero
            arg_log = (PMT_val - Rate * 0) / (PMT_val + Rate * PV_val)
            if arg_log > 0:
                NPER_fin = np.log(arg_log) / np.log(1 + Rate)
            else:
                NPER_fin = np.nan
                
        OPEXgross = 0
        LCOEgross = 1000 * (Io + OPEXgross/crf) / (Wl.X/crf) if Wl.X > 0 else 0
        
        # Almacenar los resultados de la iteración
        list_capex.append(cpv)
        list_tir.append(TIR_fin)
        list_nper.append(NPER_fin)
        list_npv.append(NPV_fin)
        list_lcoe_gross.append(LCOEgross)
        
        print(f"{cpv:<10}{TIR_fin:6.2f}%   {NPER_fin:8.2f}     {NPV_fin:12,.2f}    {LCOEgross:10.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# 6  GENERACIÓN DE GRÁFICAS INDEPENDIENTES
# ─────────────────────────────────────────────────────────────────────────────
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# Gráfica 1: TIR
plt.figure(figsize=(8, 5))
plt.plot(list_capex, list_tir, marker='o', color='crimson', linewidth=2)
plt.title('Análisis de Sensibilidad: TIR vs CAPEXpv', fontsize=12, fontweight='bold')
plt.xlabel('CAPEXpv (USD/kW)', fontsize=10)
plt.ylabel('TIR (%)', fontsize=10)
plt.tight_layout()
plt.show()

# Gráfica 2: Payback Time (PBT / NPER)
plt.figure(figsize=(8, 5))
plt.plot(list_capex, list_nper, marker='s', color='orange', linewidth=2)
plt.title('Análisis de Sensibilidad: Payback Time (PBT) vs CAPEXpv', fontsize=12, fontweight='bold')
plt.xlabel('CAPEXpv (USD/kW)', fontsize=10)
plt.ylabel('PBT (Años)', fontsize=10)
plt.tight_layout()
plt.show()

# Gráfica 3: NPV Financiero
plt.figure(figsize=(8, 5))
plt.plot(list_capex, list_npv, marker='^', color='teal', linewidth=2)
plt.title('Análisis de Sensibilidad: NPV vs CAPEXpv', fontsize=12, fontweight='bold')
plt.xlabel('CAPEXpv (USD/kW)', fontsize=10)
plt.ylabel('NPV (€)', fontsize=10)
plt.axhline(0, color='red', linestyle='--', linewidth=1) # Línea de referencia en NPV = 0
plt.tight_layout()
plt.show()

# Gráfica 4: LCOE Gross
plt.figure(figsize=(8, 5))
plt.plot(list_capex, list_lcoe_gross, marker='d', color='navy', linewidth=2)
plt.title('Análisis de Sensibilidad: Gross LCOE vs CAPEXpv', fontsize=12, fontweight='bold')
plt.xlabel('CAPEXpv (USD/kW)', fontsize=10)
plt.ylabel('Gross LCOE (€/MWh)', fontsize=10)
plt.tight_layout()
plt.show()