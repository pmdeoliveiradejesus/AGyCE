#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 10 22:35:37 2025

@author: pm.deoliveiradejes
"""

# -*- coding: utf-8 -*-
"""
Despacho óptimo Industria + BESS + PV + Electrolizador  (Caso Colombia)
Incluye las restricciones del Modelo 2 (producción de H₂ verde)
"""
import numpy as np
import numpy_financial as npf
import gurobipy as gp
from   gurobipy import GRB, quicksum
import csv 
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
w2 = 1 # 1 = net importer, 0=net exporter
Cm    = 0.1544392817773160
CAPEXpv = 770
CAPEX_BESS = 220
CAPEX_BESS_inverter = 88
CAPEXe = 440
crf       = 0.08024258719069
PenReactiva = -24942.4
# Límites SOC
SOC_up = ((1-DoD)/2 + DoD) * C
SOC_lo = ((1-DoD)/2) * C

# --- Parámetros del electrolizador (Modelo 2)
SH2        = 90        # kW  (capacidad nominal)
PH2_prod   = 90        # kW  (consumo en modo producción)
PH2_sb     = 4.5       # kW  (modo espera)
PH2_idle   = 0.45      # kW  (modo inactivo)
CMP        = 0.15      # carga parcial mínima
IA         = 11        # arranques máximos por día
eta_H2     = 50        # kWh por kg de H₂
H2_max_año    = 15768          # kg/año
H2_max_dia    = 43.2           # kg/día
H2_max_hora    = 1.8           # kg/hora
eta_H2O    = 0.015     # m³ agua / kg H₂
H2_price   = 9.4   # $/kg  (elige 4.0, 5.5, 8.0, 9.5 … según escenario)
H2O_price  = 2.75   # $/m³  (valor de la Tabla 8.2 (TESIS))

# ---------------------------------------------------------------------------
# 3.  MODELO GUROBI
# ---------------------------------------------------------------------------
m = gp.Model('AGPE_Colombia_H2')

# 3.1 VARIABLES --------------------------------------------------------------
npv = m.addVar(name='npv', lb=-GRB.INFINITY)
Base = m.addVar(name='Base', lb=-GRB.INFINITY)
CashFlow = m.addVar(name='CashFlow', lb=-GRB.INFINITY)
Investment = m.addVar(name='Investment', lb=-GRB.INFINITY)
Benefit    = m.addVar(name='Benefit',   lb=-GRB.INFINITY)
Backup     = m.addVar(name='Backup',    lb=0)
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

# ---------- Electrolizador (Modelo 2) ----------
a  = {t: m.addVar(vtype=GRB.BINARY, name=f'a[{t}]')          for t in T}   # inactivo
b  = {t: m.addVar(vtype=GRB.BINARY, name=f'b[{t}]')          for t in T}   # producción
c  = {t: m.addVar(vtype=GRB.BINARY, name=f'c[{t}]')          for t in T}   # espera
rh = {t: m.addVar(lb=0, ub=1,      name=f'rh[{t}]')         for t in T}   # carga relativa
d  = {t: m.addVar(vtype=GRB.BINARY, name=f'd[{t}]')          for t in T}
f  = {t: m.addVar(vtype=GRB.BINARY, name=f'f[{t}]')          for t in T}

P_E_prod = {t: m.addVar(lb=0, name=f'P_E_prod[{t}]') for t in T}
P_E      = {t: m.addVar(lb=0, name=f'P_E[{t}]')      for t in T}

H2_prod  = {t: m.addVar(lb=0, name=f'H2_prod[{t}]')  for t in T}
H2_total_dia = m.addVar(lb=0, name='H2_total_dia')
H2_total_año = m.addVar(lb=0, name='H2_total_año')
H2O_total_dia  = m.addVar(lb=0, name='H2O_total_dia')
H2O_total_año  = m.addVar(lb=0, name='H2O_total_año')

# 3.2 RESTRICCIONES ----------------------------------------------------------

# --- Financiero -------------------------------------------------------------
m.addConstr(
    Benefit == - Backup                        # cargo mensual por demanda
               + VE                           # ⇦ 
                     + 365*H2_price * H2_total_dia        # ingresos H₂
                     - 365*H2O_price * H2O_total_dia,        # costo agua
    name='AGPE'
)

m.addConstr(Backup == 12*kappa * Pbmax,          name='r1')
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
        Pd[t] + Pb[t] + PV_t == Pc[t] + Ps[t] + Load_t + P_E[t],
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

m.addConstr(Exc1 <= Imp, name='r11')

# ---------- RESTRICCIONES DEL ELECTROLIZADOR (Modelo 2) ----------
for t in T:
    # Estado exclusivo
    m.addConstr(a[t] + b[t] + c[t] == 1,                      name=f'h2_state[{t}]')

# Estado inicial
m.addConstr(a[1] == 1, name='h2_init_a')
m.addConstr(b[1] == 0, name='h2_init_b')
m.addConstr(c[1] == 0, name='h2_init_c')
m.addConstr(rh[1]== 0, name='h2_init_rh')

for t in T:
    # rh solo cuando b=1 y ≥ CMP
    m.addConstr(rh[t] <= b[t],                    name=f'rh_up[{t}]')
    m.addConstr(rh[t] >= CMP * b[t],              name=f'rh_lo[{t}]')

    # Potencia de producción proporcional a rh
    m.addConstr(P_E_prod[t] == PH2_prod * rh[t],  name=f'prod_power[{t}]')

    # Potencia total del electrolizador (producción + standby + idle)
    m.addConstr(P_E[t] == P_E_prod[t] + PH2_sb*c[t] + PH2_idle*a[t],
                name=f'P_E_tot[{t}]')

    # Límite de potencia instalada
    m.addConstr(P_E[t] <= SH2,                    name=f'cap_E[{t}]')

# --- Arranques máximos ----------------------------------------------------
for t in T:
    if t>1:
        m.addConstr(d[t] <= b[t])
        m.addConstr(d[t] <= a[t-1])
        m.addConstr(d[t] >= b[t] + a[t-1] - 1)
m.addConstr(quicksum(d[t] for t in T if t>1) <= IA)

# --- Variables auxiliares para transiciones (linealización simplificada) --
for t in T:
    if t > 1:
        # d = 1 si se arranca desde inactivo
        m.addConstr(d[t] <= b[t],            name=f'd1[{t}]')
        m.addConstr(d[t] <= a[t-1],          name=f'd2[{t}]')
        m.addConstr(d[t] >= b[t] + a[t-1] - 1, name=f'd3[{t}]')
        # f = 1 si transición espera→producción
        m.addConstr(f[t] <= b[t],            name=f'f1[{t}]')
        m.addConstr(f[t] <= c[t-1],          name=f'f2[{t}]')
        m.addConstr(f[t] >= b[t] + c[t-1] - 1, name=f'f3[{t}]')

# --- Producción de hidrógeno y consumo de agua ----------------------------
for t in T:
    # H₂ (kg) producido cada hora
    m.addConstr(H2_prod[t] * eta_H2 == P_E_prod[t], name=f'H2_prod[{t}]')
m.addConstr(H2_total_dia == quicksum(H2_prod[t] for t in T), name='H2_total_def')
m.addConstr(H2_total_año == 365*H2_total_dia, name='H2_total_año') 
m.addConstr(H2_prod[t] <= H2_max_hora,  name='H2_max_hora')
m.addConstr(H2O_total_dia == eta_H2O * H2_total_dia, name='H2O_total_dia')
m.addConstr(H2O_total_año ==365*H2O_total_dia, name='H2O_total_año') 

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
# 5.  RESULTADOS BÁSICOS
# ---------------------------------------------------------------------------
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
    
if m.status == gp.GRB.OPTIMAL:
    with open('solution_M1_5_E2c.csv', 'w', newline='') as csvfile:
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
    print("Solution written to solution_M1_5_E2c.csv")      