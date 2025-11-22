$title Dimensionamiento óptimo Industria+BESS+PV OnGrid (Caso Colombia, 8760h)
Set
   t 'hours'         / t1*t8760 /;
$include Ppvu8760.inc
$include Plu8760.inc
* -----------------------------------------------------
Variable
   Benefit       'Benefit USD/yr'
   VE            'Energy sold to the system USD/day'
   CashFlow      'Project CashFlow USD/yr'
   npv           'Net Present Value USD'
   Base          'Load payment with no PV and no BESS, USD';
Positive variable
   Backup        'Backup System Payment in USD/kW-yr'
   SOC(t)        'State of Charge  kWh'
   Pd(t)         'Power battery discharge  kW'
   Pc(t)         'Power battery charge  kW' 
   Pb(t)         'Power bought from the public grid kW'
   Ps(t)         'Power sold to the public grid kW'  
   Investment    'Project initial investment Eur'
   Exc1          'Exported energy Type 1 (Energy Credit) USD/day'
   Exc2          'Exported energy Type 2 (Traded with the market) USD/day'
   Imp           'Imported energy from the system USD/day'
   expo          'Exported energy kWh/yr'
   Wload         'Energia total load kWh/año'
   Wpvtot        'Producción Energia PV kWh/año'
   Wimport       'Importación Energia kWh/año'
   Wexport       'Exportación Energia kWh/año'
   WcargaBESS    'Energia carga BESS kWh/año'
   WdescargaBESS 'Energia carga BESS kWh/año'
   Ppvmax       'installed PV capacity kW'
   C             'BESS Capacity kWh'
   Pinverter     'BESS inverter size kW'
   SOC0          'Initial SOC kWh'
   Pbmax         'Contracted backup demand kW';
Binary Variable
   w1(t)         'defines if the BESS is charging or discharging'
*   w2 'defines if Exp < Imp (w2=1, Net Importer) or Exp > Imp (w2=0, Net Exporter)' 
   w3(t)        'defines if the AGPE is exporting or importing energy from the system';   
Scalar 
   Plmax     / 564.3 /
   eff_c     / 0.93 /
   eff_d     / 0.97 /
*   R_c       / 0.2/
*   R_d       / 0.2/
   DoD       / 0.9/
   Pmax      / 600 /
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
   crf       /0.08024258719069/
   ReactivePayment /-24942.4/
*   defines if Exp < Imp (w2=1, net exporter) or Exp > Imp (w2=0, net, importer)
   w2        /1/   ;
   C.LO = 500;
Equation AGPE, balance, r1, r2, r3, r4a, r4b, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16,
r16b, r17, r18, r19, r20, r21, r22, r23, r24, r25, r26, r27
*, r28, r29, r30, r31
;
AGPE..          Benefit =e=  -Backup + VE;
r1..            Backup  =e=  12*kappa*Pbmax;
r2..            Imp     =e=  sum((t),Pb(t));
r3..            expo    =e=  sum((t),Ps(t));
r4a..           Exc1    =e= w2*expo+(1-w2)*Imp;
r4b..           Exc2    =e= w2*0+(1-w2)*(expo-Imp);
r5..            VE      =e=  ((Exc1-Imp)*CU-Exc1*Co*(1-Flag)-Exc1*(Tr+Di+PR+Co+Re)*Flag+ Exc2*Cm);
balance(t)..    Pd(t) + Pb(t) + Ppvmax*data3(t,'Ppvu') - Pc(t) - Ps(t) - Plmax*data4(t,'Plu') =e= 0;
r6(t)..         SOC(t) =e= SOC0$(ord(t)=1) + SOC(t-1)$(ord(t)>1) + Pc(t)*eff_c  - Pd(t)/eff_d;
r7(t)..         Pc(t)  =l= Pinverter*w1(t);
r8(t)..         Pd(t)  =l= Pinverter*(1-w1(t));
r9(t)..         Pb(t)  =l= Pmax*w3(t);
r10(t)..        Ps(t)  =l= Pmax*(1-w3(t));
r11..           Exc1   =l= Imp;
r12(t)..        Ps(t)  =l= Pbmax;
r13..           SOC('t8760')=e= SOC0;
r14(t)..        SOC(t)  =l= ((1-DoD)/2+DoD)*C;
r15(t)..        SOC(t)  =g= ((1-DoD)/2)*C;
r16..           Pinverter=l=2*C;
r16b..          Pinverter=g=0.1*C;
r17..           SOC0=e=((1-DoD)/2)*C;
r18..           CashFlow =e= Benefit-Base;
r19..           Investment =e=    CAPEXpv*Ppvmax+CAPEX_BESS*C+CAPEX_BESS_inverter*Pinverter;
r20..           npv=e=CashFlow/crf-Investment;
r21..           Base =e=sum((t), -CU* Plmax*data4(t,'Plu'))+w2*ReactivePayment;
r22..           Wload=e=sum((t),data4(t,'Plu'))*Plmax;
r23..           Wpvtot=e=sum((t),data3(t,'Ppvu'))*Ppvmax;
r24..           Wimport=e= sum((t),Pb(t));
r25..           Wexport=e= sum((t),Ps(t));
r26..           WcargaBESS =e= sum((t),Pc(t));
r27..           WdescargaBESS =e= sum((t),Pd(t));
*r28..           C =e= 2000;
*r29..           Pinverter =e= 400;
*r30..           Ppvmax    =e= 569;
*r31..           Pbmax     =e= 400;
Model modelAGPEcolombia / all /;
solve modelAGPEcolombia using minlp maximizing npv
execute_unload 'Results M1_6_E2cL.gdx';
