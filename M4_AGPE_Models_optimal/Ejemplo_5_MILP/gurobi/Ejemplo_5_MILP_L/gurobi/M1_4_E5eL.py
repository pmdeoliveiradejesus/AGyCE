#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 10 21:15:32 2025

@author: Paulo De Oliveira (PDEOLIV@GMAIL.COM) y Alejandro Salas Durán
"""

# -*- coding: utf-8 -*-
"""
M1_4_E5eL
Despacho óptimo Industria 1 + BESS + PV  ─ Caso España - 8760h
-----------------------------------------------------------------------------
"""
import numpy as np
import numpy_financial as npf
import gurobipy as gp
from   gurobipy import GRB, quicksum
import re
import csv

def read_inc(path):
    """
    Lee un .inc con líneas 't<horas>  <valor>' y devuelve un dict.
    Ignora líneas vacías o que no empiecen por 't'.
    """
    valores = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.lstrip().startswith("t"):
                continue
            partes = re.split(r"\s+", line.strip())
            if len(partes) >= 2:
                hora  = int(partes[0][1:])          # ‘t123’ → 123
                valor = float(partes[1])
                valores[hora] = valor
    return valores

paths = {
    'lambda'  : 'lambda.inc',
#    'Plu'     : 'Plu2.inc',  # Industry 2
    'Plu'     : 'Plu.inc',    # Industry 1
    'psi'     : 'psi.inc',
#   'Ppvu'    : 'PpvuC.inc',  # Perfil Solar Colombia
    'Ppvu'    : 'PpvuE.inc',  # Perfil Solar España
    'Pbmax_p' : 'Pbmax.inc',
}

# Cargamos cada archivo en un diccionario individual
series = {nombre: read_inc(ruta) for nombre, ruta in paths.items()}

# ─────────────────────────────────────────────────────────────────────────────
# 1  CONJUNTO DE HORAS
# ─────────────────────────────────────────────────────────────────────────────
 
T = range(1, 8761)                      # t = 1 … 8760

# ─────────────────────────────────────────────────────────────────────────────
# 2  TABLA «data»  (precio spot λ, perfil de carga Plu, peaje psi, PV pu)
# ─────────────────────────────────────────────────────────────────────────────

# Si Pbmax.inc contiene un único valor constante, lo tomamos de la primera hora
pbmax_const = series['Pbmax_p'].get(1, 0.0) if len(series['Pbmax_p']) == 1 else None

data = {
    t: {
        'lambda' : series['lambda'].get(t, 0.0),
        'Plu'    : series['Plu'].get(t, 0.0),
        'psi'    : series['psi'].get(t, 0.0),
        'Ppvu'   : series['Ppvu'].get(t, 0.0),
        'Pbmax_p': series['Pbmax_p'].get(t, pbmax_const if pbmax_const is not None else 0.0),
    }
    for t in T
}
# ─────────────────────────────────────────────────────────────────────────────
# 3  ESCALARES
# ─────────────────────────────────────────────────────────────────────────────
# ── Activos eléctricos
Ppvmax = 569.0                       # kWp instalados
Plmax  = 564.3                       # kW pico de carga Industry 1
#Plmax  = 630.620646500000           # kW pico de carga Industry 2
SOC0   = 100.0                       # kWh al inicio
C      = 2000.0                      # kWh (capacidad batería)
eff_c  = 0.93                        # eficiencia carga
eff_d  = 0.97                        # eficiencia descarga
R_c    = 0.20                        # máx C-rate de carga
R_d    = 0.20                        # máx C-rate de descarga
DoD    = 0.90
Pmax   = 600.0                       # límite inverter export/import
Capacity01 = -31713.9
Capacity02 = -33786.68
CAPEXpv = 700
CAPEX_BESS = 200
CAPEX_BESS_inverter = 80
CAPEX_CDS=400
crf       = 0.08024258719069
# ── Cargos de capacidad en España (€/kW-año)
#kappaP1, kappaP2, kappaP3 = 28.79187, 15.07764,  6.55917
#kappaP4, kappaP5, kappaP6 =  5.17209,  1.93281,  0.91609
#PbmaxP1, PbmaxP2, PbmaxP3 = 504.43000000,    453.96686700,   404.47000000
#PbmaxP4, PbmaxP5, PbmaxP6 = 442.91000000,    338.0551530,    564.30000000
#capac_cost = (kappaP1*PbmaxP1 + kappaP2*PbmaxP2 + kappaP3*PbmaxP3 +
#              kappaP4*PbmaxP4 + kappaP5*PbmaxP5 + kappaP6*PbmaxP6)
kappa = [0, 28.79187, 15.07764, 6.55917, 5.17209, 1.93281, 0.91609]
peak_hours = {1:178, 2:177, 3:1847, 4:2229, 5:2247, 6:1}
# ── Límites SOC batería
SOC_up = ((1-DoD)/2 + DoD)*C
SOC_lo = ((1-DoD)/2)*C
# ─────────────────────────────────────────────────────────────────────────────
# MODELO GUROBI
# ─────────────────────────────────────────────────────────────────────────────
m = gp.Model('AG_España8760')
# VARIABLES ──────────────────────────────────────────────────────────────
Benefit = m.addVar(name='Benefit', lb=-GRB.INFINITY)
npv = m.addVar(name='npv', lb=-GRB.INFINITY)
CashFlow = m.addVar(name='CashFlow', lb=-GRB.INFINITY)
Investment = m.addVar(name='Investment', lb=-GRB.INFINITY)
Capacity  = m.addVar(name="Capacity", lb=-GRB.INFINITY)
Energy  = m.addVar(name="Capacity", lb=-GRB.INFINITY)
Base = m.addVar(name='Base', lb=-GRB.INFINITY)
Pinverter= m.addVar(name='Pinverter', lb=0)
# Batería y red
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
# FUNCIÓN DE BENEFICIO ───────────────────────────────────────────────────
m.addConstr(
    Benefit ==
        - Capacity                                           
        +  Energy,
    name='Bcalc'
)
# BALANCE ENERGÉTICO ─────────────────────────────────────────────────────
for t in T:
    m.addConstr(
        Pd[t] + Pb[t] + Ppvmax * data[t]['Ppvu'] ==
        Pc[t] + Ps[t] + Plmax * data[t]['Plu'],
        name=f'balance[{t}]'
    )
for t in T:
    if t == 1:
        m.addConstr(SOC[t] == SOC0 + Pc[t]*eff_c - Pd[t]/eff_d,
                    name=f'SOC_dyn[{t}]')
    else:
        m.addConstr(SOC[t] == SOC[t-1] + Pc[t]*eff_c - Pd[t]/eff_d,
                    name=f'SOC_dyn[{t}]')
SOC[8760].LB = SOC0
SOC[8760].UB = SOC0
for t in T:
    m.addConstr(Pc[t] <= R_c*C * w1[t],        name=f'r_Pc[{t}]')
    m.addConstr(Pd[t] <= R_d*C * (1-w1[t]),    name=f'r_Pd[{t}]')
    m.addConstr(Pb[t] <= Pmax * w3[t],         name=f'r_Pb[{t}]')
    m.addConstr(Ps[t] <= Pmax * (1-w3[t]),     name=f'r_Ps[{t}]')
    m.addConstr(Pb[t] <= data[t]['Pbmax_p'],     name=f'r_Pbmax[{t}]')
m.addConstr(
    Capacity == gp.quicksum(kappa[i]*data[peak_hours[i]]['Pbmax_p'] for i in range(1,7)),
    name="capacity"
)
m.addConstr(
   Energy ==   quicksum( data[t]['lambda'] * Ps[t]
            - (data[t]['lambda'] + data[t]['psi']) * Pb[t]
            for t in T ),
    name="energy"
  )
# ANALISIS FINANCIERO
m.addConstr(Base==-quicksum(Plmax * data[t]['Plu']*(data[t]['lambda'] + data[t]['psi']) for t in T)+Capacity01)
m.addConstr(Investment == CAPEXpv*(Ppvmax)
            +CAPEX_BESS*(C)+CAPEX_BESS_inverter*(Pinverter))
m.addConstr(Pinverter ==C*R_c)
m.addConstr(CashFlow == Benefit-Base, name='r7_1')
m.addConstr(Investment ==    CAPEXpv*Ppvmax+CAPEX_BESS*C+CAPEX_BESS_inverter*C*R_c, name='r8_1')
m.addConstr(npv == CashFlow/crf-Investment, name='r9_2')
m.addConstr(Wl == sum(Plmax * data[t]['Plu'] for t in T))
m.addConstr(Es == (quicksum(data[t]['lambda'] * Ps[t] for t in T)))
m.addConstr(Eb == (quicksum((data[t]['lambda'] + data[t]['psi']) * Pb[t] for t in T)))
m.addConstr(OPEX == Capacity + Eb )
# 4.8 OBJETIVO
m.setObjective(Benefit, GRB.MAXIMIZE)
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
    OPEXgross = 0
    LCOEgross = 1000*(Io + OPEXgross/crf)/(Wl.X/crf) if Wl.X > 0 else 0
    LCOEnet = 1000*(Io + (OPEX.X + Base.X - Es.X)/crf)/((Wl.X)/crf) if Wl.X > 0 else 0
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
    print(f"Gross LCOE: (only CAPEX and OPEX)    {LCOEgross:,.2f} €/MWh")
    print(f"Net LCOE (include earnings and savings):     {LCOEnet:,.2f} €/MWh")   
    
if m.status == gp.GRB.OPTIMAL:
    with open('solution_M1_4_E5eL.csv', 'w', newline='') as csvfile:
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
    print("Solution written to solution_M1_4_E5eL.csv")

# Optimal solution found (tolerance 1.00e-04)
# Best objective -1.877901013296e+04, best bound -1.877901013296e+04, gap 0.0000%
# Resultados:
# ---------------------
# Beneficio óptimo: -18,779.01 €/año
# NPV: 435,308.44 €/año
# Base: -120,334.71 €/año
# Investment: 830,300.00 €/año
# CashFlow: 101,555.70 €/año
# NPV:      435,308.44 €
# TIR:      10.60 %
# NPER:     10.77 años
# B/C Ratio 1.52
# Solution written to solution.csv    
    