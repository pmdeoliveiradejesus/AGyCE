#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 10 22:35:37 2025

@author: pm.deoliveiradejes
"""

# -*- coding: utf-8 -*-
"""
Despacho óptimo Industria + BESS + PV  (Caso Colombia 24h)
"""
import numpy as np
import numpy_financial as npf
import gurobipy as gp
from   gurobipy import GRB, quicksum

# ---------------------------------------------------------------------------
# 1.  CONJUNTOS Y DATOS
# ---------------------------------------------------------------------------
T = range(1, 25)                                            # 1 … 24 horas
# Tabla «data» de GAMS convertida a un diccionario Python
data = {
1	:{'Plu':	0.135388629	, 'Ppvu':	0	},
2	:{'Plu':	0.090377249	, 'Ppvu':	0	},
3	:{'Plu':	0.076343641	, 'Ppvu':	0	},
4	:{'Plu':	0.075224251	, 'Ppvu':	0	},
5	:{'Plu':	0.074307579	, 'Ppvu':	0	},
6	:{'Plu':	0.073105609	, 'Ppvu':	0	},
7	:{'Plu':	0.07340619	, 'Ppvu':	0.04749275	},
8	:{'Plu':	0.085516409	, 'Ppvu':	0.200034333	},
9	:{'Plu':	0.883664344	, 'Ppvu':	0.371942917	},
10	:{'Plu':	1        	, 'Ppvu':	0.51218625	},
11	:{'Plu':	0.967245871	, 'Ppvu':	0.605126833	},
12	:{'Plu':	0.966410238	, 'Ppvu':	0.645309833	},
13	:{'Plu':	0.122847384	, 'Ppvu':	0.627257667	},
14	:{'Plu':	0.892179316	, 'Ppvu':	0.568799917	},
15	:{'Plu':	0.96886548	, 'Ppvu':	0.47320525	},
16	:{'Plu':	0.959187873	, 'Ppvu':	0.337161417	},
17	:{'Plu':	0.947290206	, 'Ppvu':	0.188570083	},
18	:{'Plu':	0.647289021	, 'Ppvu':	0.043513583	},
19	:{'Plu':	0.627968641	, 'Ppvu':	0	},
20	:{'Plu':	0.659335617	, 'Ppvu':	0	},
21	:{'Plu':	0.581590013	, 'Ppvu':	0	},
22	:{'Plu':	0.179217943	, 'Ppvu':	0	},
23	:{'Plu':	0.144883067	, 'Ppvu':	0	},
24	:{'Plu':	0.13804102	, 'Ppvu':	0	} }
# ---------------------------------------------------------------------------
# 2.  ESCALARES
# ---------------------------------------------------------------------------
# PV + batería (sin cambios)
Ppvmax = 569.00
Plmax  = 231.241369863014
SOC0   = 100
C      = 2000
eff_c  = 0.93
eff_d  = 0.97
R_c    = 0.2
R_d    = 0.2
DoD    = 0.9
Pmax   = 600
Pbmax  = 400
Tr     = 0.013405417
Di     = 0.027124375
PR     = 0.012440625
Co     = 0.033245000
Re     = 0.004844167
CU     = 0.190428958
kappa  = 5
Flag   = 1
w2 = 1 #W2=1 NET IMPORTER W2=0 NET EXPORTER
Cm    = 0.1544392817773160
CAPEXpv = 770
CAPEX_BESS = 220
CAPEX_BESS_inverter = 88
crf       = 0.08024258719069
PenReactiva = -24942.4
# Límites SOC
SOC_up = ((1-DoD)/2 + DoD) * C
SOC_lo = ((1-DoD)/2) * C
# ---------------------------------------------------------------------------
# 3.  MODELO GUROBI
# ---------------------------------------------------------------------------
m = gp.Model('AGPE_Colombia')
# 3.1 VARIABLES --------------------------------------------------------------
npv = m.addVar(name='npv', lb=-GRB.INFINITY)
Base = m.addVar(name='Base', lb=-GRB.INFINITY)
CashFlow = m.addVar(name='CashFlow', lb=-GRB.INFINITY)
Investment = m.addVar(name='Investment', lb=-GRB.INFINITY)
Benefit    = m.addVar(name='Benefit',   lb=-GRB.INFINITY)
Backup     = m.addVar(name='Backup',    lb=-GRB.INFINITY)
VE         = m.addVar(name='VE',        lb=-GRB.INFINITY)          # beneficio energía vendida
Expo       = m.addVar(name='Expo',      lb=0)
Exc1       = m.addVar(name='Exc1',      lb=0)
Exc2       = m.addVar(name='Exc2',      lb=0)
Imp        = m.addVar(name='Imp',       lb=0)
# Batería / red
SOC = {t: m.addVar(lb=SOC_lo, ub=SOC_up, name=f'SOC[{t}]') for t in T}
Pd  = {t: m.addVar(lb=0, name=f'Pd[{t}]')  for t in T}
Pc  = {t: m.addVar(lb=0, name=f'Pc[{t}]')  for t in T}
Pb  = {t: m.addVar(lb=0, name=f'Pb[{t}]')  for t in T}
Ps  = {t: m.addVar(lb=0, name=f'Ps[{t}]')  for t in T}
w1 = {t: m.addVar(vtype=GRB.BINARY, name=f'w1[{t}]') for t in T}
w3 = {t: m.addVar(vtype=GRB.BINARY, name=f'w3[{t}]') for t in T}
# 3.2 RESTRICCIONES ----------------------------------------------------------
# --- Financiero -------------------------------------------------------------
m.addConstr(
    Benefit == -  Backup                        # cargo mensual por demanda
             +     VE ,        # costo agua
    name='AGPE'
)
m.addConstr(Backup == 12*kappa * Pbmax,name='r1')
m.addConstr(Imp    == 365*quicksum(Pb[t] for t in T),name='r2')
m.addConstr(Expo   == 365*quicksum(Ps[t] for t in T),name='r3')
m.addConstr(Exc1   == w2*Expo+(1-w2)*Imp,name='r4a')
m.addConstr(Exc2   == w2*0+(1-w2)*(Expo-Imp),name='r4b')
m.addConstr(
    VE == (Exc1 - Imp) * CU
         - Exc1 * Co * (1 - Flag)
         - Exc1 * (Tr + Di + PR + Co + Re)*Flag
         + Exc2*Cm,
    name='r5'
)

# --- Balance de potencia (incluye electrolizador) -------------------------
for t in T:
    PV_t   = Ppvmax * data[t]['Ppvu']
    Load_t = Plmax  * data[t]['Plu']
    m.addConstr(
        Pd[t] + Pb[t] + PV_t == Pc[t] + Ps[t] + Load_t,
        name=f'balance[{t}]'
    )
# --- Dinámica SOC batería -------------------------------------------------
for t in T:
    if t == 1:
        m.addConstr(SOC[t] == SOC0 + Pc[t]*eff_c - Pd[t]/eff_d, name=f'r6[{t}]')
    else:
        m.addConstr(SOC[t] == SOC[t-1] + Pc[t]*eff_c - Pd[t]/eff_d, name=f'r6[{t}]')
SOC[24].LB = SOC0
SOC[24].UB = SOC0
# --- Límites potencia batería / red ---------------------------------------
for t in T:
    m.addConstr(Pc[t] <= R_c*C * w1[t],             name=f'r7[{t}]')
    m.addConstr(Pd[t] <= R_d*C * (1 - w1[t]),       name=f'r8[{t}]')
    m.addConstr(Pb[t] <= Pmax   * w3[t],            name=f'r9[{t}]')
    m.addConstr(Ps[t] <= Pmax   * (1 - w3[t]),      name=f'r10[{t}]')
    m.addConstr(Ps[t] <= Pbmax,                     name=f'r12[{t}]')
    m.addConstr(Exc1  <= Imp,                       name='r11')
# 4.9 ANALISIS FINANCIERO
m.addConstr(CashFlow == Benefit-Base, name='r7')
m.addConstr(Investment ==    CAPEXpv*Ppvmax+CAPEX_BESS*C+CAPEX_BESS_inverter*C*R_c, name='r8')
m.addConstr(npv == CashFlow/crf-Investment, name='r9')
for t in T:
    m.addConstr(Base ==(
            -quicksum( CU * Plmax * data[t]['Plu']*365
                    for t in T )+PenReactiva 
          ), name='r10')


# ---------------------------------------------------------------------------
# 3.3  FUNCIÓN OBJETIVO
# ---------------------------------------------------------------------------
m.setObjective(Benefit, GRB.MAXIMIZE)
# ---------------------------------------------------------------------------
# 4.  OPTIMIZACIÓN
# ---------------------------------------------------------------------------
m.optimize()
# ---------------------------------------------------------------------------
# 6  RESULTADOS BÁSICOS
# ─────────────────────────────────────────────────────────────────────────────
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
    print(f"Beneficio óptimo: {Benefit.X:,.2f} USD/año")
    print(f"NPV: {npv.X:,.2f} USD/año")
    print(f"Base: {Base.X:,.2f} USD/año")
    print(f"Investment: {Investment.X:,.2f} USD/año")
    print(f"CashFlow: {S:,.2f} USD/año")
    print(f"NPV:      {NPV:,.2f} USD")   
    print(f"TIR:      {TIR:,.2f} %")
    print(f"NPER:     {NPER:,.2f} años")
    print(f"B/C Ratio {BCratio:,.2f}")