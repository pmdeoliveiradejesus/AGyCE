#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 10 21:15:32 2025

@author: pm.deoliveiradejes Paulo De Oliveira y Alejandro Salas
"""

# -*- coding: utf-8 -*-
"""
Despacho óptimo Industria + BESS + PV + Electrolizador ─ Caso España (24h)
-----------------------------------------------------------------------------
Versión con electrolizador (Modelo 2). Todas las magnitudes eléctricas son kW
(kWh para SOC) y los flujos económicos se anualizan con 365 días.
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
# 3  ESCALARES
# ─────────────────────────────────────────────────────────────────────────────
# ── Activos eléctricos
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
# ── Cargos de capacidad en España (€/kW-año)
kappaP1, kappaP2, kappaP3 = 28.79187, 15.07764,  6.55917
kappaP4, kappaP5, kappaP6 =  5.17209,  1.93281,  0.91609
PbmaxP1, PbmaxP2, PbmaxP3 = 504.43000000,    453.96686700,   404.47000000
PbmaxP4, PbmaxP5, PbmaxP6 = 442.91000000,    338.0551530,    564.30000000
capac_cost = (kappaP1*PbmaxP1 + kappaP2*PbmaxP2 + kappaP3*PbmaxP3 +
              kappaP4*PbmaxP4 + kappaP5*PbmaxP5 + kappaP6*PbmaxP6)

# ── Electrolizador PEM
SH2       = 90.0           # kW instalados
PH2_prod  = 90.0           # kW a plena carga
PH2_sb    = 4.5            # kW standby
PH2_idle  = 0.45           # kW idle
CMP       = 0.15           # carga parcial mínima
IA        = 11             # arranques máximos/día
eta_H2    = 50.0           # kWh/kg
H2_max_año    = 15768          # kg/año
H2_max_dia    = 43.2           # kg/día
H2_max_hora    = 1.8           # kg/hora
eta_H2O   = 0.015          # m³ agua / kg H₂
H2_price  = 4          # €/kg (escenario)
H2O_price = 2.5            # €/m³
Capacity0 = -31713.9
CAPEXpv = 700
CAPEX_BESS = 200
CAPEX_BESS_inverter = 80
CAPEXe = 400
crf       = 0.08024258719069

# ── Límites SOC batería
SOC_up = ((1-DoD)/2 + DoD)*C
SOC_lo = ((1-DoD)/2)*C

# ─────────────────────────────────────────────────────────────────────────────
# 4  MODELO GUROBI
# ─────────────────────────────────────────────────────────────────────────────
m = gp.Model('AGPE_España_H2')

# 4.1 VARIABLES ──────────────────────────────────────────────────────────────
npv = m.addVar(name='npv', lb=-GRB.INFINITY)
Benefit = m.addVar(name='Benefit', lb=-GRB.INFINITY)
Base = m.addVar(name='Base', lb=-GRB.INFINITY)
CashFlow = m.addVar(name='CashFlow', lb=-GRB.INFINITY)
Investment = m.addVar(name='Investment', lb=-GRB.INFINITY)
Capacity  = m.addVar(name="Capacity", lb=-GRB.INFINITY)
# Batería y red
SOC = {t: m.addVar(lb=SOC_lo, ub=SOC_up, name=f'SOC[{t}]') for t in T}
Pd  = {t: m.addVar(lb=0, name=f'Pd[{t}]')  for t in T}
Pc  = {t: m.addVar(lb=0, name=f'Pc[{t}]')  for t in T}
Pb  = {t: m.addVar(lb=0, name=f'Pb[{t}]')  for t in T}
Ps  = {t: m.addVar(lb=0, name=f'Ps[{t}]')  for t in T}

w1  = {t: m.addVar(vtype=GRB.BINARY, name=f'w1[{t}]') for t in T}
w3  = {t: m.addVar(vtype=GRB.BINARY, name=f'w3[{t}]') for t in T}

# Electrolizador (estados)
a = {t: m.addVar(vtype=GRB.BINARY, name=f'a[{t}]') for t in T}   # inactivo
b = {t: m.addVar(vtype=GRB.BINARY, name=f'b[{t}]') for t in T}   # producción
c = {t: m.addVar(vtype=GRB.BINARY, name=f'c[{t}]') for t in T}   # standby
rh = {t: m.addVar(lb=0, ub=1,      name=f'rh[{t}]') for t in T}  # carga relativa
d  = {t: m.addVar(vtype=GRB.BINARY, name=f'd[{t}]') for t in T}  # arranques

P_E_prod = {t: m.addVar(lb=0, name=f'P_E_prod[{t}]') for t in T}
P_E      = {t: m.addVar(lb=0, name=f'P_E[{t}]')      for t in T}

H2_prod  = {t: m.addVar(lb=0, name=f'H2_prod[{t}]')  for t in T}
H2_total_dia = m.addVar(lb=0, name='H2_total_dia')
H2_total_año = m.addVar(lb=0, name='H2_total_año')
H2O_total_dia  = m.addVar(lb=0, name='H2O_total_dia')
H2O_total_año  = m.addVar(lb=0, name='H2O_total_año')

# 4.2 FUNCIÓN DE BENEFICIO ───────────────────────────────────────────────────
m.addConstr(
    Benefit ==
        - capac_cost                                           # €/año (potencia)
        + 365 * (
            quicksum( data[t]['lambda'] * Ps[t]
                    - (data[t]['lambda'] + data[t]['psi']) * Pb[t]
                    for t in T )
            + H2_price  * H2_total_dia
            - H2O_price * H2O_total_dia
          ),
    name='Bcalc'
)
# 4.3 BALANCE ENERGÉTICO ─────────────────────────────────────────────────────
for t in T:
    m.addConstr(
        Pd[t] + Pb[t] + Ppvmax * data[t]['Ppvu'] ==
        Pc[t] + Ps[t] + Plmax * data[t]['Plu'] + P_E[t],
        name=f'balance[{t}]'
    )

# 4.4 DINÁMICA DEL SOC ───────────────────────────────────────────────────────
for t in T:
    if t == 1:
        m.addConstr(SOC[t] == SOC0 + Pc[t]*eff_c - Pd[t]/eff_d,
                    name=f'SOC_dyn[{t}]')
    else:
        m.addConstr(SOC[t] == SOC[t-1] + Pc[t]*eff_c - Pd[t]/eff_d,
                    name=f'SOC_dyn[{t}]')
SOC[24].LB = SOC0
SOC[24].UB = SOC0

# 4.5 BATERÍA: CARGA / DESCARGA EXCLUYENTE ───────────────────────────────────
for t in T:
    m.addConstr(Pc[t] <= R_c*C * w1[t],        name=f'r_Pc[{t}]')
    m.addConstr(Pd[t] <= R_d*C * (1-w1[t]),    name=f'r_Pd[{t}]')
    m.addConstr(Pb[t] <= Pmax * w3[t],         name=f'r_Pb[{t}]')
    m.addConstr(Ps[t] <= Pmax * (1-w3[t]),     name=f'r_Ps[{t}]')

# 4.6 LÍMITES DE POTENCIA POR BLOQUE ─────────────────────────────────────────
for t in range(1,  9):  m.addConstr(Pb[t] <= PbmaxP6, name=f'r6_13_PbmaxP6[{t}]')
m.addConstr(Pb[ 9] <= PbmaxP5, name='r14_PbmaxP5')
m.addConstr(Pb[10] <= PbmaxP3, name='r15_PbmaxP3')
for t in range(11, 15): m.addConstr(Pb[t] <= PbmaxP4, name=f'r16_19_PbmaxP4[{t}]')
for t in range(15, 19): m.addConstr(Pb[t] <= PbmaxP5, name=f'r20_23_PbmaxP5[{t}]')
m.addConstr(Pb[19] <= PbmaxP1, name='r24_PbmaxP1')
for t in range(20, 23): m.addConstr(Pb[t] <= PbmaxP2, name=f'r25_27_PbmaxP2[{t}]')
for t in range(23, 25): m.addConstr(Pb[t] <= PbmaxP5, name=f'r28_29_PbmaxP5[{t}]')

# 4.7 ELECTROLIZADOR: ESTADOS Y RESTRICCIONES ────────────────────────────────
# ---- Estados exclusivos
for t in T:
    m.addConstr(a[t] + b[t] + c[t] == 1, name=f'h2_state[{t}]')

# ---- Inicialización
m.addConstr(a[1] == 1); m.addConstr(b[1] == 0); m.addConstr(c[1] == 0)
m.addConstr(rh[1]== 0)

# ---- Carga relativa y potencia
for t in T:
    m.addConstr(rh[t] <= b[t],             name=f'rh_up[{t}]')
    m.addConstr(rh[t] >= CMP * b[t],       name=f'rh_lo[{t}]')
    m.addConstr(P_E_prod[t] == PH2_prod * rh[t],
                name=f'P_E_prod[{t}]')
    m.addConstr(P_E[t] == P_E_prod[t] + PH2_sb*c[t] + PH2_idle*a[t],
                name=f'P_E_tot[{t}]')
    m.addConstr(P_E[t] <= SH2,             name=f'cap_E[{t}]')

# ---- Arranques linealizados
for t in T:
    if t > 1:
        m.addConstr(d[t] <= b[t]);       m.addConstr(d[t] <= a[t-1])
        m.addConstr(d[t] >= b[t] + a[t-1] - 1)
m.addConstr(quicksum(d[t] for t in T if t > 1) <= IA, name='startups')

# ---- Producción H₂ y consumo agua
for t in T:
    m.addConstr(H2_prod[t] * eta_H2 == P_E_prod[t], name=f'H2_prod[{t}]')
m.addConstr(H2_total_dia == quicksum(H2_prod[t] for t in T), name='H2_total_def')
m.addConstr(H2_total_año == 365*H2_total_dia, name='H2_total_año') 
m.addConstr(H2_prod[t] <= H2_max_hora,  name='H2_max_hora')
m.addConstr(H2O_total_dia == eta_H2O * H2_total_dia, name='H2O_total_dia')
m.addConstr(H2O_total_año ==365*H2O_total_dia, name='H2O_total_año') 
# 4.8 OBJETIVO
m.setObjective(Benefit, GRB.MAXIMIZE)

# 4.9 ANALISIS FINANCIERO
m.addConstr(CashFlow == Benefit-Base, name='r7')
m.addConstr(Investment ==  CAPEXe*SH2 + CAPEXpv*Ppvmax+CAPEX_BESS*C+CAPEX_BESS_inverter*C*R_c, name='r8')
m.addConstr(npv == CashFlow/crf-Investment, name='r9')
for t in T:
    m.addConstr(Base ==(
            -quicksum((data[t]['lambda'] + data[t]['psi']) * Plmax * data[t]['Plu']*365
                    for t in T )+Capacity0
          ), name='r10')

# ─────────────────────────────────────────────────────────────────────────────
# 5  OPTIMIZACIÓN
# ─────────────────────────────────────────────────────────────────────────────
m.optimize()

# ─────────────────────────────────────────────────────────────────────────────
# 6  RESULTADOS BÁSICOS
# Basic Financial Analysis
Io = Investment.X  # CAPEX in USD
Rate = 0.05  # Discount rate (5%)
S = CashFlow.X  # OPEX
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
# ─────────────────────────────────────────────────────────────────────────────
if m.Status == GRB.OPTIMAL:
    print(f"Resultados:")
    print(f"---------------------")
    print(f"Beneficio óptimo: {Benefit.X:,.2f} €/año")
    print(f"NPV: {npv.X:,.2f} €/año")
    print(f"Base: {Base.X:,.2f} €/año")
    print(f"Investment: {Investment.X:,.2f} €/año")
    print(f"CashFlow: {S:,.2f} €/año")
    print(f"NPV:      {NPV:,.2f} €")   
    print(f"TIR:      {TIR:,.2f} %")
    print(f"NPER:     {NPER:,.2f} años")
    print(f"B/C Ratio {BCratio:,.2f}")    
    print(f"\nBeneficio óptimo  : {Benefit.X:,.2f} €/año")
    print(f"H₂ producido        : {H2_total_año.X:,.2f} kg/año  (máx {H2_max_año} kg/año)")
    print(f"H₂o consumido       : {H2O_total_año.X:,.2f} m3/año ")
else:
    print("No se alcanzó solución óptima.  Código de estado:", m.Status)
    
if m.status == gp.GRB.OPTIMAL:
    with open('solution_M1_5_E1eL.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow(["Hour", "Pb", "Ps", "Pc", "Pd", "SOC","Benefit","npv" ])
        # Write each hour's data
        for t in T:
            writer.writerow([
                t,
                Pb[t].X,
                Ps[t].X,
                Pc[t].X,
                Pd[t].X,
                SOC[t].X,
                Benefit.X,
                npv.X
            ])
    print("Solution written to solution_M1_5_E1e.csv")      