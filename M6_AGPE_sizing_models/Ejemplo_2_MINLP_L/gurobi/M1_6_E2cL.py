#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 10 22:35:37 2025

@author: pm.deoliveiradejes
"""

# -*- coding: utf-8 -*-
"""
Dimensionamiento óptimo Industria + BESS + PV   (Caso Colombia ,8760h)
"""
import numpy as np
import numpy_financial as npf
import gurobipy as gp
from   gurobipy import GRB, quicksum
import re 
import csv
def read_inc(path):
    """
    Devuelve un dict {hora:int  ->  valor:float}
    """
    valores = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            # Solo procesamos las filas que empiezan por t<número>
            if not line.lstrip().startswith("t"):
                continue
            partes = re.split(r"\s+", line.strip())
            if len(partes) >= 2:                       # ej. ['t123', '0.456']
                hora = int(partes[0][1:])              # quitamos la ‘t’
                valor = float(partes[1])
                valores[hora] = valor
    return valores

T = range(1, 8761)                      # t = 1 … 8760

# Tabla «data» de GAMS convertida a un diccionario Python
plu   = read_inc("Plu.inc")     # ó 'INDUSTRY 1'
#plu   = read_inc("Plu2.inc")     # ó 'INDUSTRY 2'
ppvu  = read_inc("PpvuC.inc")   # ó '/mnt/data/PpvuC.inc'

data = { t: {'Plu':  plu.get(t, 0.0),
             'Ppvu': ppvu.get(t, 0.0)}
         for t in T }
# ---------------------------------------------------------------------------
# 2.  ESCALARES
# ---------------------------------------------------------------------------
# PV + batería  
Plmax  = 564.3
eff_c  = 0.93
eff_d  = 0.97
DoD    = 0.9
Pmax   = 600
Tr     = 0.013405417
Di     = 0.027124375
PR     = 0.012440625
Co     = 0.033245000
Re     = 0.004844167
CU     = 0.190428958
kappa  = 5
Flag   = 1 # Flag=1 AGPE mayor a 100kW
w2 = 1  #w=0 #net exporter, w=1, net importer
Cm    = 0.1544392817773160
CAPEXpv = 770
CAPEX_BESS = 220
CAPEX_BESS_inverter = 88
crf       = 0.08024258719069
ReactivePayment = -24942.4
# ---------------------------------------------------------------------------
# 3.  MODELO GUROBI
# ---------------------------------------------------------------------------
m = gp.Model('AGPE_Colombia')
# 3.1 VARIABLES --------------------------------------------------------------
Benefit    = m.addVar(name='Benefit',   lb=-GRB.INFINITY)
Backup     = m.addVar(name='Backup',    lb=-GRB.INFINITY)
VE         = m.addVar(name='VE',        lb=-GRB.INFINITY)          # beneficio energía vendida
Expo       = m.addVar(name='Expo',      lb=0)
Exc1       = m.addVar(name='Exc1',      lb=0)
Exc2       = m.addVar(name='Exc2',      lb=0)
Imp        = m.addVar(name='Imp',       lb=0)
npv = m.addVar(name='npv', lb=-GRB.INFINITY)
Benefit = m.addVar(name='Benefit', lb=-GRB.INFINITY)
Base = m.addVar(name='Base', lb=-GRB.INFINITY)
CashFlow = m.addVar(name='CashFlow', lb=-GRB.INFINITY)
Investment = m.addVar(name='Investment', lb=0)
Pinverter = m.addVar(name='Pinverter', lb=0)
Pbmax = m.addVar(name='Pbmax', lb=0)
Ppvmax = m.addVar(name='Ppvmax', lb=0)
SOC0 = m.addVar(name='SOC0', lb=0)
C = m.addVar(name='C', lb=500)
# Batería / red
SOC = {t: m.addVar(lb=0, name=f'SOC[{t}]') for t in T}
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
m.addConstr(Imp    == quicksum(Pb[t] for t in T),name='r2')
m.addConstr(Expo   == quicksum(Ps[t] for t in T),name='r3')
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
# --- Límites potencia batería / red ---------------------------------------
for t in T:
    m.addConstr(Pc[t] <= Pinverter * w1[t],             name=f'r7[{t}]')
    m.addConstr(Pd[t] <= Pinverter * (1 - w1[t]),       name=f'r8[{t}]')
    m.addConstr(Pb[t] <= Pmax   * w3[t],            name=f'r9[{t}]')
    m.addConstr(Ps[t] <= Pmax   * (1 - w3[t]),      name=f'r10[{t}]')
    m.addConstr(Ps[t] <= Pbmax,                     name=f'r12[{t}]')
    m.addConstr(Exc1  <= Imp,                       name='r11')
    
m.addConstr(SOC0 == ((1-DoD)/2)*C, name='r3')
m.addConstr(SOC0 == SOC[8760], name='r4')
m.addConstr(Pinverter <=C*2.0)
m.addConstr(Pinverter >=C*0.2)

for t in T:
    m.addConstr(SOC[t] <=  ((1-DoD)/2 + DoD)*C, name='r5')
    m.addConstr(SOC[t] >=  ((1-DoD)/2)*C, name='r6')
 
# 4.9 ANALISIS FINANCIERO
m.addConstr(CashFlow == Benefit-Base, name='r7')
m.addConstr(Investment ==    CAPEXpv*Ppvmax+CAPEX_BESS*C+CAPEX_BESS_inverter*Pinverter, name='r8')
m.addConstr(npv == CashFlow/crf-Investment, name='r9')
for t in T:
    m.addConstr(Base ==(
            -quicksum( CU * Plmax * data[t]['Plu']
                    for t in T )+ w2*ReactivePayment
          ), name='r10')
# m.addConstr(C == 2000, name='r10')
# m.addConstr(Pinverter == 400, name='r11')
# m.addConstr(Ppvmax  == 569, name='r12')
# m.addConstr(Pbmax   == 400, name='r13')    
# ---------------------------------------------------------------------------
# 3.3  FUNCIÓN OBJETIVO
# ---------------------------------------------------------------------------
m.setObjective(npv, GRB.MAXIMIZE)
# Net importer (w2=1) ---------------------
# Beneficio óptimo: -40,722.88 €/año
# NPV: 1,422,658.35 €/año
# C: 861.91 kWh
# Pinverter:  233.15 kW
# C-rate:  0.27 kW
# Ppvmax:  581.71 kW
# Pbmax: 277.75 kW
# Base: -207,685.02 €/año
# Investment: 658,058.91 €/año
# CashFlow: 166,962.14 €/año
# NPV:      1,422,658.35 €
# TIR:      25.08 %
# NPER:     4.50 años
# B/C Ratio 3.16


# Net exporter (w2=0) ---------------------
# Beneficio óptimo: 381,331.35 €/año
# NPV: 3,512,791.61 €/año
# C: 7,518.04 kWh
# Pinverter:  1,503.61 kW
# Ppvmax:  2,247.44 kW
# Pbmax: 600.00 kW
# Base: -182,742.62 €/año
# Investment: 3,516,816.79 €/año
# CashFlow: 564,073.97 €/año
# NPV:      3,512,791.61 €
# TIR:      15.07 %
# NPER:     7.66 años
# B/C Ratio 2.00

# ---------------------------------------------------------------------------
# 4.  OPTIMIZACIÓN
# ---------------------------------------------------------------------------
m.optimize()
# ---------------------------------------------------------------------------
# 5.  RESULTADOS BÁSICOS
# ---------------------------------------------------------------------------
Crate = Pinverter.X/C.X
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
    if w2==1:
        print(f"Exportador Neto (w2=1)") 
    else:
        print(f"Importador Neto (w2=0)") 
    print(f"Beneficio óptimo: {Benefit.X:,.2f} €/año")
    print(f"NPV: {npv.X:,.2f} €/año")
    print(f"C: {C.X:,.2f} kWh")
    print(f"Pinverter:  {Pinverter.X:,.2f} kW")
    print(f"C-rate:  {Crate:,.2f} kW")
    print(f"Ppvmax:  {Ppvmax.X:,.2f} kW")
    print(f"Pbmax: {Pbmax.X:,.2f} kW")   
    print(f"Base: {Base.X:,.2f} €/año")
    print(f"Investment: {Investment.X:,.2f} €/año")
    print(f"CashFlow: {S:,.2f} €/año")
    print(f"NPV:      {NPV:,.2f} €")   
    print(f"TIR:      {TIR:,.2f} %")
    print(f"NPER:     {NPER:,.2f} años")
    print(f"B/C Ratio {BCratio:,.2f}")


else:
    print("\nNo se alcanzó solución óptima (código de estado: ", m.Status, ")")
    
if m.status == gp.GRB.OPTIMAL:
    with open('solution_M1_6_E2cL.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow(["Hour", "Pb", "Ps", "Pc", "Pd", "SOC",	
"Benefit","npv" ])
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
    print("Solution written to solution_M1_6_E2cL.csv")        