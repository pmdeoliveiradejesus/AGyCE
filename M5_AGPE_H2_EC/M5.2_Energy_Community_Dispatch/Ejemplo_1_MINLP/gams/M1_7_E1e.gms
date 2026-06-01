$title M_1_7_E1e Energy Community 1 and 2 with a CDS - Dispatch MINLP (spain 24h)
*M1.7.E1e - Caso España:  CE+CDS with PV+BESS (OnGrid) (Despacho Optimo, 24h)
Set
   t 'hours'         / t1*t24 /;
Table data(t,*)
*    Eur/kWh            per unit            Eur/kWh         per unit 
    lambda              psi                 Ppvu                Plu2                  pbmax2         Plu1               pbmax1
t1  0.068746794520548   0.0228205053080510  0.000000000000000   0.530061285794532   553.88960000000 0.135388629090637   564.3000000
t2  0.064382931506849   0.0228205053080510  0.000000000000000   0.531661233031055   553.88960000000 0.090377249176867   564.3000000
t3  0.062238410958904   0.0228205053080510  0.000000000000000   0.534176029026283   553.88960000000 0.076343641406536   564.3000000
t4  0.060464136986301   0.0228205053080510  0.000000000000000   0.553334784117771   553.88960000000 0.075224251241957   564.3000000
t5  0.060655534246575   0.0228205053080510  0.000000000000000   0.618973516973413   553.88960000000 0.074307578750070   564.3000000
t6  0.065132136986301   0.0228205053080510  0.000000000000000   0.732698140959379   553.88960000000 0.073105608680250   564.3000000
t7  0.073826082191781   0.0228205053080510  0.047492750000000   0.905410448254070   553.88960000000 0.073406190057000   564.3000000
t8  0.076148794520548   0.0228205053080510  0.200034333333333   0.989775313849690   553.88960000000 0.085516408757498   564.3000000
t9  0.069382712328767   0.0210743713052406  0.371942916666667   1.000000000000000   379.49780000000 0.883664344082149   338.0551530
t10 0.056760082191781   0.0319883482993510  0.512186250000000   0.980132084762807   494.17200000000 1.000000000000000   404.4700000
t11 0.046949369863014   0.0221906474349675  0.605126833333333   0.957725277555312   561.32090000000 0.967245871300936   442.9100000
t12 0.041846739726027   0.0221906474349675  0.645309833333333   0.942323657709171   561.32090000000 0.966410238486499   442.9100000
t13 0.039593726027397   0.0221906474349675  0.627257666666667   0.913475812983633   561.32090000000 0.122847383567665   442.9100000
t14 0.037885123287671   0.0221906474349675  0.568799916666667   0.889945957227714   561.32090000000 0.892179315688642   442.9100000
t15 0.036840931506849   0.0210743713052406  0.473205250000000   0.886750273145298   379.49780000000 0.968865480059381   338.0551530
t16 0.038253698630137   0.0210743713052406  0.337161416666667   0.905656297371664   379.49780000000 0.959187873431187   338.0551530
t17 0.046423205479452   0.0210743713052406  0.188570083333333   0.861890166282270   379.49780000000 0.947290206165413   338.0551530
t18 0.059484767123288   0.0210743713052406  0.043513583333333   0.701714201302491   379.49780000000 0.647289021374806   338.0551530
t19 0.076155178082192   0.0720344854462120  0.000000000000000   0.351262364643030   408.15430000000 0.627968640962237   504.4300000
t20 0.090286438356164   0.0512182441617940  0.000000000000000   0.338840454837792   437.71230000000 0.659335616819762   453.9668670
t21 0.099023506849315   0.0512182441617940  0.000000000000000   0.317456333765505   437.71230000000 0.581590012689108   453.9668670
t22 0.090372109589041   0.0512182441617940  0.000000000000000   0.293644351056787   437.71230000000 0.179217943416770   453.9668670
t23 0.081188794520548   0.0210743713052406  0.000000000000000   0.274768244366155   379.49780000000 0.144883067091137   338.0551530
t24 0.074767232876712   0.0210743713052406  0.000000000000000   0.331848323823927   379.49780000000 0.138041019820362   338.0551530;  
* -----------------------------------------------------
PARAMETER
pbmax1(t)
Plu1(t)
pbmax2(t)
Plu2(t);
pbmax1(t) = data(t,'pbmax1');
Plu1(t) =   data(t,'Plu1');
pbmax2(t) = data(t,'pbmax2');
Plu2(t) =   data(t,'Plu2');;   
Variable
   npv         'Net Present Value Eur Industry 1+2'
   Benefit1     'Benefit Eur/year'
   Capacity1    'Capacity Payment Eur/year'
   Energy1      'Energy Trading Result Eur/year'
   CashFlow1    'Project CashFlow Eur/yr'
   npv1         'Net Present Value Eur Industry 1'
   Base1        'Load payment with no PV and no BESS'
   Benefit2     'Benefit Eur/year'
   Capacity2    'Capacity Payment Eur/year'
   Energy2      'Energy Trading Result Eur/year'
   CashFlow2    'Project CashFlow Eur/yr'
   npv2         'Net Present Value Eur Industry 1'
   Base2        'Load payment with no PV and no BESS'
   IndustryProfit   'Total Industry 1 + 2 Profit, Euro/year'
   CW               'Total Community Welfare, Euro/year'
   EP1              'Energy and Power/Capacity Balance Industry 1 Euro/year'
   EP2              'Energy and Power/Capacity Balance Industry 2 Euro/year'
   E1               'Exchange Industry 1 with the Aggregaror, Euro/year'
   E2               'Exchange Industry 2 with the Aggregaror, Euro/year'
   APA              'CDS Aggregator Profit, Euro,/year'
   I1_Profit        'Industry 1 Profit with respect to no CDS, Euro,/year'
   I2_Profit        'Industry 2 Profit with respect to no CDS, Euro,/year'
   AP1              'Industry 1 Profit, Euro,/year'
   AP2              'Industry 2 Profit, Euro,/year'
Positive variable
   SOC1(t)      'State of Charge  kWh'
   Pd1(t)       'Power battery discharge  kW'
   Pc1(t)       'Power battery charge  kW' 
   Pb1(t)       'Power bought from the public grid kW'
   Ps1(t)       'Power sold to the public grid kW'  
   Investment1  'Project initial investment Eur'
   Wload1       'Energia total load kWh/año'
   Wpvtot1      'Producción Energia PV kWh/año'
   Wimport1      'Importación Energia kWh/año'
   Wexport1      'Exportación Energia kWh/año'
   WcargaBESS1  'Energia carga BESS kWh/año'
   WdescargaBESS1  'Energia carga BESS kWh/año'
   SOC2(t)      'State of Charge  kWh'
   Pd2(t)       'Power battery discharge  kW'
   Pc2(t)       'Power battery charge  kW' 
   Pb2(t)       'Power bought from the public grid kW'
   Ps2(t)       'Power sold to the public grid kW'  
   Investment2  'Project initial investment Eur'
   Wload2       'Energia total load kWh/año'
   Wpvtot2      'Producción Energia PV kWh/año'
   Wimport2      'Importación Energia kWh/año'
   Wexport2      'Exportación Energia kWh/año'
   WcargaBESS2  'Energia carga BESS kWh/año'
   WdescargaBESS2  'Energia carga BESS kWh/año'
   P12CDS(t)       'Power sent from 1 to 2 through a CDS kW'
   P21CDS(t)       'Power sent from 2 to 1 through a CDS kW'
   epsilon(t)      'Internal Local Market Price $/kWh'
   delta        'Internal Capacity Price $/kW';
Binary Variable
   w11     
   w31
   w12     
   w32
   v12;
Scalar 
   Ppvmax1    / 569/
   Plmax1     / 231.241369863014 /
   SOC01      / 100  /
   C1         / 2000  /
   eff_c1     / 0.93 /
   eff_d1     / 0.97 /
   R_c1       / 0.2/
   R_d1       / 0.2/
   DoD1       / 0.9/
   Pmax1      / 600/
   Capacity01    /-31713.9/
   Ppvmax2    / 800/
   Plmax2     / 312.78235978049 /
   SOC02      / 140  /
   C2         / 2800  /
   eff_c2     / 0.92 /
   eff_d2     / 0.95 /
   R_c2       / 0.3/
   R_d2       / 0.3/
   DoD2       / 0.9/
   Pmax2      / 650/
   Capacity02    /-33786.68/
   kappaP1   / 28.79187 /
   kappaP2   / 15.07764 /
   kappaP3   / 6.55917 /
   kappaP4   / 5.17209 /
   kappaP5   / 1.93281 /
   kappaP6   / 0.91609 /
   CAPEXpv   /700/
   CAPEX_BESS /200/
   CAPEX_BESS_inverter /80/
   crf       /0.08024258719069/
   varphib      /0.00375/
   varphis      /0.00125/ 
   PmaxCDS     / 400/
   CAPEX_I1   /830300/
   CAPEX_I2   /1187200/
;
*Limits
SOC1.up(t)     = ((1-DoD1)/2+DoD1)*C1;
SOC1.lo(t)     = ((1-DoD1)/2)*C1;
SOC1.fx('t24') = SOC01;
SOC2.up(t)     = ((1-DoD2)/2+DoD2)*C2;
SOC2.lo(t)     = ((1-DoD2)/2)*C2;
SOC2.fx('t24') = SOC02;
Equation BcalcA, Bcalc1A, Bcalc2A, balanceA,  r1A, r2A, r3A, r4A,r5A, r6A, r7A, r8A, r9A, r10A, r11A,r12A,r13A,r14A,r15A,r16A,
         BcalcB, Bcalc1B, Bcalc2B, balanceB,  r1B, r2B, r3B, r4B,r5B, r6B, r7B, r8B, r9B, r10B, r11B,r12B,r13B,r14B,r15B,r16B,
CE0 ,
CE1 ,
CE2 ,
CE3 ,
CE4 ,
CE5 ,
CE6 ,
CE7 ,
CE8 ,
CE9 ,
CE10    ,
CE10b    ,
CE11    ,
CE12    ,
CE13    ,
CE14    ,
CE15    ,
CE16    ,
CE17    ,
CE18    ,
CE19    ,
CE20    ,
CE21    ,
CE24;
BcalcA..         Benefit1  =e= Capacity1+Energy1;
Bcalc1A..        Capacity1 =e= -kappaP1*pbmax1('t19')-kappaP2*pbmax1('t20')-kappaP3*pbmax1('t10')-kappaP4*pbmax1('t11')-kappaP5*pbmax1('t24')-kappaP6*pbmax1('t1');
Bcalc2A..        Energy1 =e=365*sum((t), (data(t,'lambda')*ps1(t)-(data(t,'lambda')+data(t,'psi'))*pb1(t)));
balanceA(t)..    Pd1(t) + Pb1(t) + Ppvmax1*data(t,'Ppvu') - Pc1(t) - Ps1(t) - Plmax1*Plu1(t) + P21CDS(t) - P12CDS(t)=e= 0;
r1A(t)..         SOC1(t) =e= SOC01$(ord(t)=1) + SOC1(t-1)$(ord(t)>1) + Pc1(t)*eff_c1  - Pd1(t)/eff_d1;
r2A(t)..  Pc1(t) =l= R_c1*C1*w11(t);
r3A(t)..  Pd1(t) =l= R_d1*C1*(1-w11(t));
r4A(t)..  Pb1(t) =l= Pmax1*w31(t);
r5A(t)..  Ps1(t) =l= Pmax1*(1-w31(t));
r6A(t)..  pbmax1(t) =g= Pb1(t);
r7A..     CashFlow1 =e= Benefit1-Base1;
r8A..     Investment1 =e=    CAPEXpv*Ppvmax1+CAPEX_BESS*C1+CAPEX_BESS_inverter*C1*R_c1;
r9A..     npv1=e=CashFlow1/crf-Investment1;
r10A..    Base1 =e=365*sum((t), -(data(t,'lambda')+data(t,'psi'))* Plmax1*Plu1(t))+Capacity01;
r11A..    Wload1=e=365*sum((t),Plu1(t))*Plmax1;
r12A..    Wpvtot1=e=365*sum((t),data(t,'Ppvu'))*Ppvmax1;
r13A..    Wimport1=e= 365*sum((t),Pb1(t));
r14A..    Wexport1=e= 365*sum((t),Ps1(t));
r15A..    WcargaBESS1 =e= 365*sum((t),Pc1(t));
r16A..    WdescargaBESS1 =e= 365*sum((t),Pd1(t));
BcalcB..         Benefit2  =e= Capacity2+Energy2;
Bcalc1B..        Capacity2 =e= -kappaP1*pbmax2('t19')-kappaP2*pbmax2('t20')-kappaP3*pbmax2('t10')-kappaP4*pbmax2('t11')-kappaP5*pbmax2('t24')-kappaP6*pbmax2('t1');
Bcalc2B..        Energy2 =e=365*sum((t), (data(t,'lambda')*ps2(t)-(data(t,'lambda')+data(t,'psi'))*pb2(t)));
balanceB(t)..    Pd2(t) + Pb2(t) + Ppvmax2*data(t,'Ppvu') - Pc2(t) - Ps2(t) - Plmax2*Plu2(t) - P21CDS(t) + P12CDS(t) =e= 0;
r1B(t)..         SOC2(t) =e= SOC02$(ord(t)=1) + SOC2(t-1)$(ord(t)>1) + Pc2(t)*eff_c2  - Pd2(t)/eff_d2;
r2B(t)..  Pc2(t) =l= R_c2*C2*w12(t);
r3B(t)..  Pd2(t) =l= R_d2*C2*(1-w12(t));
r4B(t)..  Pb2(t) =l= Pmax2*w32(t);
r5B(t)..  Ps2(t) =l= Pmax2*(1-w32(t));
r6B(t)..  pbmax2(t) =g= Pb2(t);
r7B..     CashFlow2 =e= Benefit2-Base2;
r8B..     Investment2 =e=    CAPEXpv*Ppvmax2+CAPEX_BESS*C2+CAPEX_BESS_inverter*C2*R_c2;
r9B..     npv2=e=CashFlow2/crf-Investment2;
r10B..    Base2 =e=365*sum((t), -(data(t,'lambda')+data(t,'psi'))* Plmax2*Plu2(t))+Capacity02;
r11B..    Wload2=e=365*sum((t),Plu2(t))*Plmax2;
r12B..    Wpvtot2=e=365*sum((t),data(t,'Ppvu'))*Ppvmax2;
r13B..    Wimport2=e= 365*sum((t),Pb2(t));
r14B..    Wexport2=e= 365*sum((t),Ps2(t));
r15B..    WcargaBESS2 =e= 365*sum((t),Pc2(t));
r16B..    WdescargaBESS2 =e= 365*sum((t),Pd2(t));
CE0..         IndustryProfit =e=  I1_Profit+ I2_Profit;
CE1..         CW =e=  EP1+E1+EP2+E2+APA; 
CE2..         EP1 =e= Benefit1;
CE3..         EP2 =e= Benefit2; 
CE4.. E1 =e=  365*(sum((t), (epsilon(t)-varphis)*P12CDS(t))-sum((t), (epsilon(t)+varphib)*P21CDS(t)));
CE5.. E2 =e=  365*(sum((t), (epsilon(t)-varphis)*P21CDS(t))-sum((t), (epsilon(t)+varphib)*P12CDS(t)));
CE6..         APA  =e=(2*delta)*PmaxCDS+(365)*(sum((t), (varphis+varphib)*(P12CDS(t)+P21CDS(t))));
CE7..         I1_Profit =e= EP1+E1;
CE8..         I2_Profit =e= EP2+E2;
CE9..         AP1=e= EP1+E1;
CE10..        AP2=e= EP2+E2;
CE10b..       Investment2*I1_Profit=e=Investment1*I2_Profit;
CE11(t)..      P12CDS(t) =l= PmaxCDS*v12(t);
CE12(t)..      P21CDS(t) =l= PmaxCDS*(1-v12(t));
CE13(t)..      epsilon(t) =l= (data(t,'lambda')+data(t,'psi'));
CE14(t)..      epsilon(t) =g= data(t,'lambda');
CE15..      delta =l= kappaP1;
CE16..      delta =l= kappaP2;
CE17..      delta =l= kappaP3;
CE18..      delta =l= kappaP4;
CE19..      delta =l= kappaP5;
CE20..      delta =l= kappaP6;
CE21..      delta =g= 0;
CE24..      npv=e=(IndustryProfit-Base1-Base2)/crf-Investment1-Investment2;
*option minlp=lindo, miqcp=lindo;
*option minlp=alphaecp, miqcp=alphaecp;
*option minlp=knitro, miqcp=knitro;
*option minlp=lindoglobal, miqcp=lindoglobal;
*option minlp=sbb, miqcp=sbb;
*option minlp=scip, miqcp=scip;
*option minlp=shot, miqcp=shot;
*option minlp=xpress, miqcp=xpress;
option minlp=gurobi, miqcp=gurobi;
Model modelCDS / all /;
solve modelCDS using MINLP maximizing IndustryProfit
execute_unload 'M1_7_E1e.gdx';
