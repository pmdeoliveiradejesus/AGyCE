$title Despacho óptimo Industria+BESS+PV OnGrid (Caso Colombia ,24H)
Set
   t 'hours'         / t1*t24 /;

Table data(t,*)
*       per unit            per unit            USD/kWh (XM 2024)
        Plu                 Ppvu                lambda
t1      0.135388629090637   0.000000000000000   0.1586041451975490
t2      0.090377249176867   0.000000000000000   0.1217198153796440
t3      0.076343641406536   0.000000000000000   0.1190982516810140
t4      0.075224251241957   0.000000000000000   0.1160118975714240
t5      0.074307578750070   0.000000000000000   0.1184892975714240
t6      0.073105608680250   0.000000000000000   0.1242799509960820
t7      0.073406190057000   0.047492750000000   0.1243378325029310
t8      0.085516408757498   0.200034333333333   0.1306424242837530
t9      0.883664344082149   0.371942916666667   0.1376351153796440
t10     1.000000000000000   0.512186250000000   0.1401095797632050
t11     0.967245871300936   0.605126833333333   0.1443161345577260
t12     0.966410238486499   0.645309833333333   0.1478920468864930
t13     0.122847383567665   0.627257666666667   0.1479728318180000
t14     0.892179315688642   0.568799916666667   0.1485314667495070
t15     0.968865480059381   0.473205250000000   0.1513679722289590
t16     0.959187873431187   0.337161416666667   0.1522125852426570
t17     0.947290206165413   0.188570083333333   0.1506114811330680
t18     0.647289021374806   0.043513583333333   0.1484249605851230
t19     0.627968640962237   0.000000000000000   0.1589462482563560
t20     0.659335616819762   0.000000000000000   0.1631816996262190
t21     0.581590012689108   0.000000000000000   0.1568946133248490
t22     0.179217943416770   0.000000000000000   0.1483866982563560
t23     0.144883067091137   0.000000000000000   0.1400058133248490
t24     0.138041019820362   0.000000000000000   0.1345652879823840;  
* -----------------------------------------------------

Variable
   Benefit     'Benefit USD/yr'
   VE          'Energy sold to the system USD/day'
   CashFlow    'Project CashFlow USD/yr'
   npv         'Net Present Value USD'
   Base        'Load payment with no PV and no BESS, USD';
Positive variable
   Backup      'Backup System Payment in USD/kW-yr'
   SOC(t)      'State of Charge  kWh'
   Pd(t)       'Power battery discharge  kW'
   Pc(t)       'Power battery charge  kW' 
   Pb(t)       'Power bought from the public grid kW'
   Ps(t)       'Power sold to the public grid kW'  
   Investment  'Project initial investment Eur'
   Exc1        'Exported energy Type 1 (Energy Credit) USD/day'
   Exc2        'Exported energy Type 2 (Traded with the market) USD/day'
   Imp         'Imported energy from the system USD/day'
   expo        'Exported energy kWh/yr'
   Wload       'Energia total load kWh/año'
   Wpvtot      'Producción Energia PV kWh/año'
   Wimport      'Importación Energia kWh/año'
   Wexport      'Exportación Energia kWh/año'
   WcargaBESS    'Energia carga BESS kWh/año'
   WdescargaBESS  'Energia carga BESS kWh/año';
Binary Variable
   w1(t)       'defines if the BESS is charging or discharging'
*   w2          'defines if Exp < Imp (w2=1) or Exp > Imp (w2=0)' 
   w3(t)       'defines if the AGPE is exporting or importing energy from the system';   
Scalar 
   Ppvmax    / 569/   
   Plmax     / 231.241369863014 /
   SOC0      / 100  /
   C         / 2000  /
   eff_c     / 0.93 /
   eff_d     / 0.97 /
   R_c       / 0.2/
   R_d       / 0.2/
   DoD       / 0.9/
   Pmax      / 600 /
   Pbmax     / 400/
   Tr        /  0.013405417/
   Di        / 0.027124375/
   PR        / 0.012440625/
   Co        / 0.033245000/
   Re        / 0.004844167/
   CU        / 0.190428958/
   kappa     / 5/
   Flag      / 1/
   Cm        /0.1544392817773160/
   CAPEXpv   /770/
   CAPEX_BESS /220/
   CAPEX_BESS_inverter /88/
   ReactivePayment /-24942.4/
   crf       /0.08024258719069/
   w2        /0/   ;
SOC.up(t)     = ((1-DoD)/2+DoD)*C;
SOC.lo(t)     = ((1-DoD)/2)*C;
SOC.fx('t24') = SOC0;
Equation AGPE, balance, r1, r2, r3, r4a, r4b, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19, r20, r21, r22;
AGPE..         Benefit =e=  -Backup + VE;
r1..           Backup  =e=  12*kappa*Pbmax;
r2..           Imp     =e=  365*sum((t),Pb(t));
r3..           expo    =e=  365*sum((t),Ps(t));
r4a..           Exc1    =e= w2*expo+(1-w2)*Imp;
r4b..           Exc2    =e= (1-w2)*(expo-Imp);
r5..           VE      =e=  ((Exc1-Imp)*CU-Exc1*Co*(1-Flag)-Exc1*(Tr+Di+PR+Co+Re)*Flag+ Exc2*Cm);
balance(t)..   Pd(t) + Pb(t) + Ppvmax*data(t,'Ppvu') - Pc(t) - Ps(t) - Plmax*data(t,'Plu') =e= 0;
r6(t)..        SOC(t) =e= SOC0$(ord(t)=1) + SOC(t-1)$(ord(t)>1) + Pc(t)*eff_c  - Pd(t)/eff_d;
r7(t)..        Pc(t)  =l= R_c*C*w1(t);
r8(t)..        Pd(t)  =l= R_d*C*(1-w1(t));
r9(t)..        Pb(t)  =l= Pmax*w3(t);
r10(t)..       Ps(t)  =l= Pmax*(1-w3(t));
r11..          Exc1   =l= Imp;
r12(t)..       Ps(t)  =l= Pbmax;
r13..    CashFlow =e= Benefit-Base;
r14..    Investment =e=    CAPEXpv*Ppvmax+CAPEX_BESS*C+CAPEX_BESS_inverter*C*R_c;
r15..    npv=e=CashFlow/crf-Investment;
r16..    Base =e=365*sum((t), -CU* Plmax*data(t,'Plu'))+ReactivePayment;
r17..    Wload=e=365*sum((t),data(t,'Plu'))*Plmax;
r18..    Wpvtot=e=365*sum((t),data(t,'Ppvu'))*Ppvmax;
r19..    Wimport=e= 365*sum((t),Pb(t));
r20..    Wexport=e= 365*sum((t),Ps(t));
r21..    WcargaBESS =e= 365*sum((t),Pc(t));
r22..    WdescargaBESS =e= 365*sum((t),Pd(t));
option mip=gurobi, minlp=gurobi, miqcp=gurobi;  
Model modelAGPEcolombia / all /;
solve modelAGPEcolombia using mip maximizing benefit
execute_unload 'Results M1_4_E6c.gdx';
