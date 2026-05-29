#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de sensibilidad del CAPEX PV sobre KPIs (TIR, PBT, NPV, LCOEgross)
Caso: Colombia 24h (Excedentes Tipo 1, Net Importer)
"""
import numpy as np
import numpy_financial as npf
import gurobipy as gp
from gurobipy import GRB, quicksum
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1.  CONJUNTOS Y DATOS
# ---------------------------------------------------------------------------
T = range(1, 25)                                            # 1 … 24 horas

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
# 2.  ESCALARES CONSTANTES
# ---------------------------------------------------------------------------
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
w2     = 1  # W2=1 NET IMPORTER
Cm     = 0.1544392817773160
CAPEX_BESS = 220
CAPEX_BESS_inverter = 88
crf       = 0.08024258719069
PenReactiva = -24942.4

SOC_up = ((1-DoD)/2 + DoD) * C
SOC_lo = ((1-DoD)/2) * C

# ---------------------------------------------------------------------------
# 3.  RANGO DE SENSIBILIDAD
# ---------------------------------------------------------------------------
capex_pv_range = np.arange(300, 1001, 25)

list_capex = []
list_tir = []
list_nper = []
list_npv = []
list_lcoe_gross = []

print("Ejecutando análisis de sensibilidad para Colombia...")
print(f"{'CAPEXpv':<10}{'TIR (%)':<10}{'PBT (Años)':<12}{'NPV (USD)':<15}{'LCOE Gross':<12}")
print("-" * 60)

# ---------------------------------------------------------------------------
# 4.  BUCLE DE SIMULACIÓN
# ---------------------------------------------------------------------------
for cpv in capex_pv_range:
    m = gp.Model('AGPE_Colombia')
    m.Params.OutputFlag = 0  # Desactivar logs de Gurobi
    
    # VARIABLES
    npv_var = m.addVar(name='npv', lb=-GRB.INFINITY)
    Base = m.addVar(name='Base', lb=-GRB.INFINITY)
    CashFlow_var = m.addVar(name='CashFlow', lb=-GRB.INFINITY)
    Investment = m.addVar(name='Investment', lb=-GRB.INFINITY)
    Benefit    = m.addVar(name='Benefit',   lb=-GRB.INFINITY)
    Backup     = m.addVar(name='Backup',    lb=-GRB.INFINITY)
    VE         = m.addVar(name='VE',        lb=-GRB.INFINITY)
    Expo       = m.addVar(name='Expo',      lb=0)
    Exc1       = m.addVar(name='Exc1',      lb=0)
    Exc2       = m.addVar(name='Exc2',      lb=0)
    Imp        = m.addVar(name='Imp',       lb=0)
    
    SOC = {t: m.addVar(lb=SOC_lo, ub=SOC_up, name=f'SOC[{t}]') for t in T}
    Pd  = {t: m.addVar(lb=0, name=f'Pd[{t}]')  for t in T}
    Pc  = {t: m.addVar(lb=0, name=f'Pc[{t}]')  for t in T}
    Pb  = {t: m.addVar(lb=0, name=f'Pb[{t}]')  for t in T}
    Ps  = {t: m.addVar(lb=0, name=f'Ps[{t}]')  for t in T}
    w1  = {t: m.addVar(vtype=GRB.BINARY, name=f'w1[{t}]') for t in T}
    w3  = {t: m.addVar(vtype=GRB.BINARY, name=f'w3[{t}]') for t in T}
    Wl  = m.addVar(name='Wl', lb=0)
    Es  = m.addVar(name='Es', lb=0)
    Eb  = m.addVar(name='Eb', lb=0)
    OPEX = m.addVar(name='OPEX', lb=0)
    
    # RESTRICCIONES
    m.addConstr(Benefit == - Backup + VE, name='AGPE')
    m.addConstr(Backup == 12*kappa * Pbmax, name='r1')
    m.addConstr(Imp    == 365*quicksum(Pb[t] for t in T), name='r2')
    m.addConstr(Expo   == 365*quicksum(Ps[t] for t in T), name='r3')
    m.addConstr(Exc1   == w2*Expo + (1-w2)*Imp, name='r4a')
    m.addConstr(Exc2   == w2*0 + (1-w2)*(Expo-Imp), name='r4b')
    
    m.addConstr(
        VE == (Exc1 - Imp) * CU
             - Exc1 * Co * (1 - Flag)
             - Exc1 * (Tr + Di + PR + Co + Re)*Flag
             + Exc2 * Cm,
        name='r5'
    )
    
    # Balance de potencia
    for t in T:
        PV_t   = Ppvmax * data[t]['Ppvu']
        Load_t = Plmax  * data[t]['Plu']
        m.addConstr(Pd[t] + Pb[t] + PV_t == Pc[t] + Ps[t] + Load_t, name=f'balance[{t}]')
        
    # Dinámica SOC
    for t in T:
        if t == 1:
            m.addConstr(SOC[t] == SOC0 + Pc[t]*eff_c - Pd[t]/eff_d, name=f'r6[{t}]')
        else:
            m.addConstr(SOC[t] == SOC[t-1] + Pc[t]*eff_c - Pd[t]/eff_d, name=f'r6[{t}]')
    SOC[24].LB = SOC0
    SOC[24].UB = SOC0
    
    # Límites batería / red
    for t in T:
        m.addConstr(Pc[t] <= R_c*C * w1[t],        name=f'r7[{t}]')
        m.addConstr(Pd[t] <= R_d*C * (1 - w1[t]),  name=f'r8[{t}]')
        m.addConstr(Pb[t] <= Pmax   * w3[t],       name=f'r9[{t}]')
        m.addConstr(Ps[t] <= Pmax   * (1 - w3[t]), name=f'r10[{t}]')
        m.addConstr(Ps[t] <= Pbmax,                name=f'r12[{t}]')
    m.addConstr(Exc1 <= Imp, name='r11')
    
    # ANÁLISIS FINANCIERO (Utiliza 'cpv' dinámico)
    m.addConstr(CashFlow_var == Benefit - Base, name='r7_fin')
    m.addConstr(Investment == cpv*Ppvmax + CAPEX_BESS*C + CAPEX_BESS_inverter*C*R_c, name='r8_fin')
    m.addConstr(npv_var == CashFlow_var/crf - Investment, name='r9_fin')
    
    for t in T:
        m.addConstr(Base == (
                -quicksum(CU * Plmax * data[t]['Plu']*365 for t in T) + PenReactiva 
              ), name='r10_fin')
        
    m.addConstr(Wl == 365*sum(Plmax * data[t]['Plu'] for t in T))
    m.addConstr(Es == 365*(quicksum(CU * Ps[t] for t in T)))
    m.addConstr(Eb == 365*(quicksum(CU * Pb[t] for t in T)))
    m.addConstr(OPEX == Eb)
    
    m.setObjective(Benefit, GRB.MAXIMIZE)
    m.optimize()
    
    # Evaluación de resultados óptimos
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
            arg_log = (PMT_val - Rate * 0) / (PMT_val + Rate * PV_val)
            if arg_log > 0:
                NPER_fin = np.log(arg_log) / np.log(1 + Rate)
            else:
                NPER_fin = np.nan
                
        OPEXgross = 0
        LCOEgross = 1000 * (Io + OPEXgross/crf) / (Wl.X/crf) if Wl.X > 0 else 0
        
        # Almacenamiento indexado
        list_capex.append(cpv)
        list_tir.append(TIR_fin)
        list_nper.append(NPER_fin)
        list_npv.append(NPV_fin)
        list_lcoe_gross.append(LCOEgross)
        
        print(f"{cpv:<10}{TIR_fin:6.2f}%   {NPER_fin:8.2f}     {NPV_fin:12,.2f}    {LCOEgross:10.2f}")

# ---------------------------------------------------------------------------
# 5.  GENERACIÓN DE GRÁFICAS INDEPENDIENTES
# ---------------------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# Gráfica 1: TIR
plt.figure(figsize=(8, 5))
plt.plot(list_capex, list_tir, marker='o', color='forestgreen', linewidth=2)
plt.title('Análisis de Sensibilidad: TIR vs CAPEXpv (Colombia)', fontsize=12, fontweight='bold')
plt.xlabel('CAPEXpv (USD/kW)', fontsize=10)
plt.ylabel('TIR (%)', fontsize=10)
plt.tight_layout()
plt.show()

# Gráfica 2: Payback Time (PBT / NPER)
plt.figure(figsize=(8, 5))
plt.plot(list_capex, list_nper, marker='s', color='darkorange', linewidth=2)
plt.title('Análisis de Sensibilidad: Payback Time (PBT) vs CAPEXpv (Colombia)', fontsize=12, fontweight='bold')
plt.xlabel('CAPEXpv (USD/kW)', fontsize=10)
plt.ylabel('PBT (Años)', fontsize=10)
plt.tight_layout()
plt.show()

# Gráfica 3: NPV Financiero
plt.figure(figsize=(8, 5))
plt.plot(list_capex, list_npv, marker='^', color='darkblue', linewidth=2)
plt.title('Análisis de Sensibilidad: NPV vs CAPEXpv (Colombia)', fontsize=12, fontweight='bold')
plt.xlabel('CAPEXpv (USD/kW)', fontsize=10)
plt.ylabel('NPV (USD)', fontsize=10)
plt.axhline(0, color='red', linestyle='--', linewidth=1)
plt.tight_layout()
plt.show()

# Gráfica 4: LCOE Gross
plt.figure(figsize=(8, 5))
plt.plot(list_capex, list_lcoe_gross, marker='d', color='purple', linewidth=2)
plt.title('Análisis de Sensibilidad: Gross LCOE vs CAPEXpv (Colombia)', fontsize=12, fontweight='bold')
plt.xlabel('CAPEXpv (USD/kW)', fontsize=10)
plt.ylabel('Gross LCOE (USD/MWh)', fontsize=10)
plt.tight_layout()
plt.show()