$title  Despacho óptimo Industria+BESS+PV OnGrid (Caso España)
*M1.4.Ej5e - Caso España:   PV+BESS (OnGrid)  Despacho Optimo
Set
   t 'hours'         / t1*t24 /;
Table data(t,*)
*    Eur/kWh            Eur/kWh             per unit            per unit            kW
    lambda               psi                Ppvu                 Plu                Pbmax
t1  0.068746794520548   0.0228205053080510  0.000000000000000   0.135388629090637   564.30000000000
t2  0.064382931506849   0.0228205053080510  0.000000000000000   0.090377249176867   564.30000000000
t3  0.062238410958904   0.0228205053080510  0.000000000000000   0.076343641406536   564.30000000000
t4  0.060464136986301   0.0228205053080510  0.000000000000000   0.075224251241957   564.30000000000
t5  0.060655534246575   0.0228205053080510  0.000000000000000   0.074307578750070   564.30000000000
t6  0.065132136986301   0.0228205053080510  0.000000000000000   0.073105608680250   564.30000000000
t7  0.073826082191781   0.0228205053080510  0.047492750000000   0.073406190057000   564.30000000000
t8  0.076148794520548   0.0228205053080510  0.200034333333333   0.085516408757498   564.30000000000
t9  0.069382712328767   0.0210743713052406  0.371942916666667   0.883664344082149   338.05515300000
t10 0.056760082191781   0.0319883482993510  0.512186250000000   1.000000000000000   404.47000000000
t11 0.046949369863014   0.0221906474349675  0.605126833333333   0.967245871300936   442.91000000000
t12 0.041846739726027   0.0221906474349675  0.645309833333333   0.966410238486499   442.91000000000
t13 0.039593726027397   0.0221906474349675  0.627257666666667   0.122847383567665   442.91000000000
t14 0.037885123287671   0.0221906474349675  0.568799916666667   0.892179315688642   442.91000000000
t15 0.036840931506849   0.0210743713052406  0.473205250000000   0.968865480059381   338.05515300000
t16 0.038253698630137   0.0210743713052406  0.337161416666667   0.959187873431187   338.05515300000
t17 0.046423205479452   0.0210743713052406  0.188570083333333   0.947290206165413   338.05515300000
t18 0.059484767123288   0.0210743713052406  0.043513583333333   0.647289021374806   338.05515300000
t19 0.076155178082192   0.0720344854462120  0.000000000000000   0.627968640962237   504.43000000000
t20 0.090286438356164   0.0512182441617940  0.000000000000000   0.659335616819762   453.96686700000
t21 0.099023506849315   0.0512182441617940  0.000000000000000   0.581590012689108   453.96686700000
t22 0.090372109589041   0.0512182441617940  0.000000000000000   0.179217943416770   453.96686700000
t23 0.081188794520548   0.0210743713052406  0.000000000000000   0.144883067091137   338.05515300000
t24 0.074767232876712   0.0210743713052406  0.000000000000000   0.138041019820362   338.05515300000;  
* -----------------------------------------------------
PARAMETER
pbmax(t);           
pbmax(t) = data(t,'Pbmax');
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
   WdescargaBESS  'Energia carga BESS kWh/año';
Binary Variable
   w1(t)     
   w3(t);     
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
SOC.fx('t24') = SOC0;
Equation Bcalc, Bcalc1, Bcalc2, balance,  r1, r2, r3, r4,r5, r6, r7, r8, r9, r10, r11,r12,r13,r14,r15,r16;
Bcalc..         Benefit  =e= Capacity+Energy;
Bcalc1..        Capacity =e= -kappaP1*pbmax('t19')-kappaP2*pbmax('t20')-kappaP3*pbmax('t10')-kappaP4*pbmax('t11')-kappaP5*pbmax('t24')-kappaP6*pbmax('t1');
Bcalc2..        Energy =e=365*sum((t), (data(t,'lambda')*ps(t)-(data(t,'lambda')+data(t,'psi'))*pb(t)));
balance(t)..    Pd(t) + Pb(t) + Ppvmax*data(t,'Ppvu') - Pc(t) - Ps(t) - Plmax*data(t,'Plu') =e= 0;
r1(t)..         SOC(t) =e= SOC0$(ord(t)=1) + SOC(t-1)$(ord(t)>1) + Pc(t)*eff_c  - Pd(t)/eff_d;
r2(t)..  Pc(t) =l= R_c*C*w1(t);
r3(t)..  Pd(t) =l= R_d*C*(1-w1(t));
r4(t)..  Pb(t) =l= Pmax*w3(t);
r5(t)..  Ps(t) =l= Pmax*(1-w3(t));
r6(t)..  pbmax(t) =g= Pb(t);
r7..     CashFlow =e= Benefit-Base;
r8..     Investment =e=    CAPEXpv*Ppvmax+CAPEX_BESS*C+CAPEX_BESS_inverter*C*R_c;
r9..     npv=e=CashFlow/crf-Investment;
r10..    Base =e=365*sum((t), -(data(t,'lambda')+data(t,'psi'))* Plmax*data(t,'Plu'))+Capacity0;
r11..    Wload=e=365*sum((t),data(t,'Plu'))*Plmax;
r12..    Wpvtot=e=365*sum((t),data(t,'Ppvu'))*Ppvmax;
r13..    Wimport=e= 365*sum((t),Pb(t));
r14..    Wexport=e= 365*sum((t),Ps(t));
r15..    WcargaBESS =e= 365*sum((t),Pc(t));
r16..    WdescargaBESS =e= 365*sum((t),Pd(t));
*option mip=gurobi minlp=gurobi, miqcp=gurobi;
*option mip=lindo;
*option mip=clpex;
Model modelAGspain / all /;
solve modelAGspain using mip maximizing Benefit
execute_unload 'Results M1_4_E5e.gdx';
