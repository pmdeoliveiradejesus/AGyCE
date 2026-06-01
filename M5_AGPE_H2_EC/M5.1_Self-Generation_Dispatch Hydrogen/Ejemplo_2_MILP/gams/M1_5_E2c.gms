$TITLE Despacho óptimo Industria + BESS + PV + Electrolizador (Colombia, 24h)
*─────────────────────────────────────────────────────────────────────────────
* 1. CONJUNTOS
*─────────────────────────────────────────────────────────────────────────────
SET t  'horas del día' / t1*t24 / ;
*─────────────────────────────────────────────────────────────────────────────
* 2. DATOS
*─────────────────────────────────────────────────────────────────────────────
TABLE data(t,*)  ' Plu, Ppvu lambda'
     Plu                Ppvu                 lambda     
t1   0.135388629090637   0.000000000000000   0.1586041451975490
t2   0.090377249176867   0.000000000000000   0.1217198153796440
t3   0.076343641406536   0.000000000000000   0.1190982516810140
t4   0.075224251241957   0.000000000000000   0.1160118975714240
t5   0.074307578750070   0.000000000000000   0.1184892975714240
t6   0.073105608680250   0.000000000000000   0.1242799509960820
t7   0.073406190057000   0.047492750000000   0.1243378325029310
t8   0.085516408757498   0.200034333333333   0.1306424242837530
t9   0.883664344082149   0.371942916666667   0.1376351153796440
t10  1.000000000000000   0.512186250000000   0.1401095797632050
t11  0.967245871300936   0.605126833333333   0.1443161345577260
t12  0.966410238486499   0.645309833333333   0.1478920468864930
t13  0.122847383567665   0.627257666666667   0.1479728318180000
t14  0.892179315688642   0.568799916666667   0.1485314667495070
t15  0.968865480059381   0.473205250000000   0.1513679722289590
t16  0.959187873431187   0.337161416666667   0.1522125852426570
t17  0.947290206165413   0.188570083333333   0.1506114811330680
t18  0.647289021374806   0.043513583333333   0.1484249605851230
t19  0.627968640962237   0.000000000000000   0.1589462482563560
t20  0.659335616819762   0.000000000000000   0.1631816996262190
t21  0.581590012689108   0.000000000000000   0.1568946133248490
t22  0.179217943416770   0.000000000000000   0.1483866982563560
t23  0.144883067091137   0.000000000000000   0.1400058133248490
t24  0.138041019820362   0.000000000000000   0.1345652879823840;;
PARAMETER
Plu(t)   'perfil de carga'        /     / ,
Ppvu(t)  'perfil PV'              /     / ,
lam(t)   'precio spot'            /     / ;
Plu(t)  = data(t,'Plu')  ;
Ppvu(t) = data(t,'Ppvu') ;
*lam(t)  = data(t,'lambda')  ;
*─────────────────────────────────────────────────────────────────────────────
* 3. ESCALARES
*─────────────────────────────────────────────────────────────────────────────
SCALAR
   Ppvmax   / 569 /
   Plmax    / 231.241369863014 /
   SOC0     / 100  /,   C /2000/
   eff_c /0.93/,  eff_d /0.97/
   R_c /0.2/,     R_d /0.2/,     DoD /0.9/
   Pmax /600/,    Pbmax /400/
   Tr /0.013405417/, Di /0.027124375/, PR /0.012440625/
   Co /0.033245/,  Re /0.004844167/, CU /0.190428958/
   kappa /5/,      Flag /1/
   Cm    /0.1544392817773160/, w2        /1/,
   CAPEXpv   /770/,
   CAPEX_BESS /220/,
   CAPEX_BESS_inverter /88/,
   CAPEX_H2   /440/, ReactivePayment /-24942.4/,
   crf       /0.08024258719069/
* Electrolizador
   SH2 /90/, PH2_prod /90/, PH2_sb /4.5/, PH2_idle /0.45/
   CMP /0.15/, IA /11/, eta_H2 /50/, H2_max_hora /1.8/
   eta_H2O /0.015/, H2_price /9.4/, H2O_price /2.75/ ;
SCALAR SOCAR, SOCTOP ;
SOCAR  = ((1-DoD)/2)*C ;
SOCTOP = SOCAR + DoD*C ;
*─────────────────────────────────────────────────────────────────────────────
* 4. VARIABLES
*─────────────────────────────────────────────────────────────────────────────
POSITIVE VARIABLE
   SOC(t), Pd(t), Pc(t), Pb(t), Ps(t)
   P_E(t), P_E_prod(t), H2_prod(t), H2_total_dia, H2_total_anual, H2O_total_anual,
   Exc1, Exc2, Imp, expo, H2O_total_dia,rh(t), Investment;  
BINARY VARIABLE
   w1(t), w3(t),
*   w2          'defines if Expo < Imp (w2=1) or Expo > Imp (w2=0)'
   aE(t), bE(t), csE(t),           
   dE(t), fE(t) ;
VARIABLE Benefit
   VE               'Excedentes (Arbitraje) USD/año'
   Backup           'Cargos de Potencia, USD/año'
   Hidrogeno        'balance de hidrogeno, USD/año'
   CashFlow         'Project CashFlow Eur/yr'
   npv              'Net Present Value Eur'
   Base             'Load payment with no PV and no BESS Eur'
   Wload            'Energia total load kWh/año'
   Wpvtot           'Producción Energia PV kWh/año'
   Wimport          'Importación Energia kWh/año'
   Wexport          'Exportación Energia kWh/año'
   WcargaBESS       'Energia carga BESS kWh/año'
   WdescargaBESS    'Energia carga BESS kWh/año'
   Welectrolizador  'Energia consumida por el electrolizador kWh/año';
SOC.UP(t) = SOCTOP ;
SOC.LO(t) = SOCAR ;
SOC.FX('t24') = SOC0 ;
Ps.UP(t)  = Pbmax ;
*─────────────────────────────────────────────────────────────────────────────
* 5. ECUACIONES
*─────────────────────────────────────────────────────────────────────────────
EQUATION
   obj
r1  ,
r2  ,
r3  ,
r4  ,
r5  ,
r6  ,
r7  ,
r8  ,
r9  ,
r10 ,
r11 ,
r12 ,
r13 ,
r14 ,
r15 ,
r16 ,
r17 ,
r18 ,
r19 ,
r20 ,
r21 ,
r22 ,
r23 ,
r24 ,
r25 ,
r26 ,
r27 ,
r30 ,
r31 ,
r32 ,
r33 ,
r34 ,
r35 ,
r36 ,
r37 ,
r38 ,
r39 ,
r40 ,
r41 ,
r42 ,
r43 ,
r44 ,
r45 ,
r46 ,
r47 ,
r48 ,
r49 ,
r50 ,
r51 ,
r52 ;
* Objetivo
obj..               Benefit =e= -Backup+VE+Hidrogeno ;
r1..                VE =e=  ((Exc1-Imp)*CU-Exc1*Co*(1-Flag)-Exc1*(Tr+Di+PR+Co+Re)*Flag+ Exc2*Cm);
r2..                Hidrogeno =e= 365*(H2_price*H2_total_dia- H2O_price*H2O_total_dia);
r3..                Backup =e= 12*kappa*Pbmax ;
r4(t)..             Pd(t) + Pb(t) + Ppvmax*Ppvu(t) =e= Pc(t) + Ps(t) + P_E(t) + Plmax*Plu(t) ;
r5..                SOC('t1') =e= SOC0 + Pc('t1')*eff_c - Pd('t1')/eff_d ;
r6(t)$(ord(t)>1)..  SOC(t) =e= SOC(t-1) + Pc(t)*eff_c - Pd(t)/eff_d ;
r7(t)..             Pc(t) =l= R_c*C*w1(t) ;
r8(t)..             Pd(t) =l= R_d*C*(1-w1(t)) ;
r9(t)..             Pb(t) =l= Pmax*w3(t) ;
r10(t)..            Ps(t) =l= Pmax*(1-w3(t)) ;
r11..               Imp     =e=  365*sum((t),Pb(t));
r12..               expo    =e=  365*sum((t),Ps(t));
r13..               Exc1    =e= w2*expo+(1-w2)*Imp;  
r14..               Exc2    =e= w2*0+(1-w2)*(expo-Imp);;
r15..               Exc1   =l= Imp ;
*── Electrolizador
r16(t)..            aE(t) + bE(t) + csE(t) =e= 1 ;
r17..               aE('t1')=E= 1 ;
r18..               bE('t1')=E= 0 ;
r19..               csE('t1')=E= 0 ;
r20..               rh('t1')=E= 0 ;
r21(t)..            rh(t) =l= bE(t) ;
r22(t)..            rh(t) =g= CMP*bE(t) ;
r23(t)..            P_E_prod(t) =e= PH2_prod*rh(t) ;
r24(t)..            P_E(t) =e= P_E_prod(t) + PH2_sb*csE(t) + PH2_idle*aE(t) ;
r25(t)..            P_E(t) =l= SH2 ;
r26(t)..            H2_prod(t)*eta_H2 =e= P_E_prod(t) ;
r27..               H2_total_dia =e= SUM(t, H2_prod(t)) ;
r30..               H2_total_anual =e= 365*SUM(t, H2_prod(t)) ;
r31(t)..            H2_prod(t) =l= H2_max_hora;
r32..               H2O_total_dia =e= eta_H2O*H2_total_dia ;
r33..               H2O_total_anual =e= 365*H2O_total_dia ;
r34(t)$(ord(t)>1).. dE(t) =l= bE(t) ;
r35(t)$(ord(t)>1).. dE(t) =l= aE(t-1) ;
r36(t)$(ord(t)>1).. dE(t) =g= bE(t) + aE(t-1) - 1 ;
r37(t)$(ord(t)>1).. fE(t) =l= bE(t) ;
r38(t)$(ord(t)>1).. fE(t) =l= csE(t-1) ;
r39(t)$(ord(t)>1).. fE(t) =g= bE(t) + csE(t-1) - 1 ;
r40..               SUM(t$(ord(t)>1), dE(t)) =l= IA ;
r41..               CashFlow =e= -Backup+VE+Hidrogeno-Base;
r42..               Investment =e=    CAPEXpv*Ppvmax+CAPEX_BESS*C+CAPEX_BESS_inverter*C*R_c+CAPEX_H2*SH2;
r43..               npv=e=CashFlow/crf-Investment;
r44..               Base =e=sum((t), -365*CU*Plmax*data(t,'Plu'))+ReactivePayment;
r45(t)..            Pbmax =g= Pb(t);
r46..               Wload=e=sum((t),data(t,'Plu'))*Plmax;
r47..               Wpvtot=e=sum((t),data(t,'Ppvu'))*Ppvmax;
r48..               Wimport=e= sum((t),Pb(t));
r49..               Wexport=e= sum((t),Ps(t));
r50..               WcargaBESS =e= sum((t),Pc(t));
r51..               WdescargaBESS =e= sum((t),Pd(t));
r52..               Welectrolizador =e= sum((t),P_E(t)); 
option mip=gurobi, minlp=gurobi, miqcp=gurobi;
*─────────────────────────────────────────────────────────────────────────────
* 6. MODELO Y SOLVE
*─────────────────────────────────────────────────────────────────────────────
MODEL AGPE_H2 / ALL / ;
SOLVE AGPE_H2 USING MIP MAXIMIZING Benefit;
*─────────────────────────────────────────────────────────────────────────────
* 7. GUARDAR RESULTADOS
*─────────────────────────────────────────────────────────────────────────────
EXECUTE_UNLOAD 'Results_M1_5_E2c.gdx' ;
