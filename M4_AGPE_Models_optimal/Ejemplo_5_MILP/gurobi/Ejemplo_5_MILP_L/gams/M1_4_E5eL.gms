$title  Despacho óptimo Industria+BESS+PV OnGrid (Caso España) Simulación Completa 8760 horas (Precios/Solar2024) 
*M1.4.E5eL - Caso España:   PV+BESS (OnGrid)  Despacho Optimo
Set
   t 'hours'         / t1*t8760 /;
$include lambda.inc
$include psi.inc
* Registro Solar España
$include PpvuE.inc
* Registro Solar Colombia
*$include PpvuC.inc
*---------
$include Plu.inc
$include Plu2.inc
$include Pbmax.inc

* -----------------------------------------------------
PARAMETER
pbmax(t)
Plu(t);
pbmax(t) = data5(t,'Pbmax');
* Industry 1
 Plu(t) = data4(t,'PLu');
* Industry 2
*  Plu(t) = data7(t,'PLu2');

Variable
   Benefit     'Benefit Eur/year'
   Capacity    'Capacity Payment Eur/year'
   Energy      'Energy Trading Result Eur/year'
   CashFlow    'Project CashFlow Eur/yr'
   npv         'Net Present Value Eur'
   Base        'Load payment with no PV and no BESS';
Positive variable
   SOC(t)      'State of Charge  kWh'
   Pd(t)       'Power battery discharge  kW'
   Pc(t)       'Power battery charge  kW' 
   Pb(t)       'Power bought from the public grid kW'
   Ps(t)       'Power sold to the public grid kW'  
   Investment  'Project initial investment Eur'
   Wload       'Energia total load kWh/año'
   Wpvtot      'Producción Energia PV kWh/año'
   Wimport      'Importación Energia kWh/año'
   Wexport      'Exportación Energia kWh/año'
   WcargaBESS  'Energia carga BESS kWh/año'
   WdescargaBESS  'Energia carga BESS kWh/año'
   ;
Binary Variable
   w1(t)     
   w3(t);     
Scalar 
   Ppvmax    / 569/
* Industry 1   
   Plmax     / 564.3 /
* Industry 2   
*   Plmax     / 630.620646500000 /
   SOC0      / 100  /
   C         / 2000  /
   eff_c     / 0.93 /
   eff_d     / 0.97 /
   R_c       / 0.2/
   R_d       / 0.2/
   DoD       / 0.9/
   kappaP1   / 28.79187 /
   kappaP2   / 15.07764 /
   kappaP3   / 6.55917 /
   kappaP4   / 5.17209 /
   kappaP5   / 1.93281 /
   kappaP6   / 0.91609 /
   Pmax      / 600/
   CAPEXpv   /700/
   CAPEX_BESS /200/
   CAPEX_BESS_inverter /80/
   crf       /0.08024258719069/
   Capacity0    /-31713.9/;
SOC.up(t)     = ((1-DoD)/2+DoD)*C;
SOC.lo(t)     = ((1-DoD)/2)*C;
SOC.fx('t8760') = SOC0;
Equation Bcalc, Bcalc1, Bcalc2, balance,  r1, r2, r3, r4,r5, r6, r7, r8, r9, r10, r11,r12,r13,r14, r15, r16;
Bcalc..         Benefit  =e= Capacity+Energy;
Bcalc1..        Capacity =e= -kappaP1*pbmax('t178')-kappaP2*pbmax('t177')-kappaP3*pbmax('t1847')-kappaP4*pbmax('t2229')-kappaP5*pbmax('t2247')-kappaP6*pbmax('t1');
Bcalc2..        Energy =e=sum((t), (data(t,'lambda')*ps(t)-(data(t,'lambda')+data2(t,'psi'))*pb(t)));
balance(t)..    Pd(t) + Pb(t) + Ppvmax*data3(t,'Ppvu') - Pc(t) - Ps(t) - Plmax*Plu(t) =e= 0;
r1(t)..         SOC(t) =e= SOC0$(ord(t)=1) + SOC(t-1)$(ord(t)>1) + Pc(t)*eff_c  - Pd(t)/eff_d;
r2(t)..  Pc(t) =l= R_c*C*w1(t);
r3(t)..  Pd(t) =l= R_d*C*(1-w1(t));
r4(t)..  Pb(t) =l= Pmax*w3(t);
r5(t)..  Ps(t) =l= Pmax*(1-w3(t));
r6(t)..  pbmax(t) =g= Pb(t);
r7..     CashFlow =e= Benefit-Base;
r8..     Investment =e=    CAPEXpv*Ppvmax+CAPEX_BESS*C+CAPEX_BESS_inverter*C*R_c;
r9..     npv=e=CashFlow/crf-Investment;
r10..    Base =e=sum((t), -(data(t,'lambda')+data2(t,'psi'))* Plmax*Plu(t))+Capacity0;
r11..    Wload=e=sum((t),Plu(t))*Plmax;
r12..    Wpvtot=e=sum((t),data3(t,'Ppvu'))*Ppvmax;
r13..    Wimport=e= sum((t),Pb(t));
r14..    Wexport=e= sum((t),Ps(t));
r15..    WcargaBESS =e= sum((t),Pc(t));
r16..    WdescargaBESS =e= sum((t),Pd(t));
*option mip=lindo;
Model modelAGspain / all /;
solve modelAGspain using mip maximizing Benefit
execute_unload 'Results M1_4_E5eL.gdx';
