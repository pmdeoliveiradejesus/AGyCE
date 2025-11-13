$TITLE Despacho óptimo Industria + BESS + PV + Electrolizador (España)
*---------------------------------------------------------------------------
* 1  CONJUNTOS
*---------------------------------------------------------------------------
SET t  'horas del día' / t1*t24 / ;
*---------------------------------------------------------------------------
* 2  DATOS
*---------------------------------------------------------------------------
TABLE data(t,*)  'λ   psi  Ppvu Plu '
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
t24 0.074767232876712   0.0210743713052406  0.000000000000000   0.138041019820362   338.05515300000;  ;  

PARAMETER
lam(t)           'precio spot Eur/kWh'
Plu(t)           'perfil de carga'
tariff(t)        'peajes y cargos Eur/kWh'
Ppvu(t)          'perfil fotovoltaico pu'
pbmax(t)         'demanda máxima contratada kW';           
pbmax(t) = data(t,'Pbmax');
lam(t)   = data(t,'lambda');
Plu(t)   = data(t,'Plu');
tariff(t)= data(t,'psi');
Ppvu(t)  = data(t,'Ppvu');
*---------------------------------------------------------------------------
* 3  ESCALARES
*---------------------------------------------------------------------------
SCALAR
   Ppvmax / 569 / ,    Plmax / 231.241369863014 /
   SOC0   / 100  / ,   C     / 2000 /
   eff_c  / 0.93 / ,   eff_d / 0.97 /
   R_c    / 0.20 / ,   R_d   / 0.20 / ,  DoD / 0.90 /
   Pmax   / 600  / 
* cargos de capacidad
   kappaP1 /28.79187/, kappaP2 /15.07764/, kappaP3 /6.55917/,
   kappaP4 /5.17209/,  kappaP5 /1.93281/, kappaP6 /0.91609/,
   CAPEXpv   /700/,
   CAPEX_BESS /200/,
   CAPEX_BESS_inverter /80/,
   CAPEX_H2   /400/,
   crf       /0.08024258719069/,
   Capacity0    /-31713.9/ 
* electrolizador
   SH2 /90/, PH2_prod /90/, PH2_sb /4.5/, PH2_idle /0.45/,
   CMP /0.15/, IA /11/,
   eta_H2 /50/, H2_max_dia /43.2/, H2_max_hora /1.800/, eta_H2O /0.015/,
   H2_price /4/, H2O_price /2.5/ ;
SCALAR SOCLO, SOCHI ;
SOCLO = ((1-DoD)/2)*C ;
SOCHI = SOCLO + DoD*C ;
*---------------------------------------------------------------------------
* 4  VARIABLES
*---------------------------------------------------------------------------
POSITIVE VARIABLE
   SOC(t), Pc(t), Pd(t), Pb(t), Ps(t),
   P_E(t), P_E_prod(t), rh(t),
   H2_prod(t), H2_total_dia,H2_total_anual, H2O_total_dia,H2O_total_anual,Investment;
BINARY VARIABLE
   w1(t), w3(t),  aE(t), bE(t), csE(t), dE(t), fE(t) ;
VARIABLE Benefit
   Capacity     'Cargos de Poyencia, Eur/kWh'
   Arbitraje    'arbitraje con la red'
   Hidrogeno    'balance de hidrogeno'
   CashFlow     'Project CashFlow Eur/yr'
   npv          'Net Present Value Eur'
   Base         'Load payment with no PV and no BESS Eur'
   Wload       'Energia total load kWh/año'
   Wpvtot      'Producción Energia PV kWh/año'
   Wimport      'Importación Energia kWh/año'
   Wexport      'Exportación Energia kWh/año'
   WcargaBESS    'Energia carga BESS kWh/año'
   WdescargaBESS  'Energia carga BESS kWh/año'
   Welectrolizador 'Energia consumida por el electrolizador kWh/año';
* límites directos
SOC.LO(t) = SOCLO ; SOC.UP(t) = SOCHI ; SOC.FX('t24') = SOC0 ;
*---------------------------------------------------------------------------
* 5  ECUACIONES
*---------------------------------------------------------------------------
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
r28 ,
r29 ,
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
r45 ;
*––– OBJETIVO (beneficio mensual) ––––––––––––––––––––––––––––––––––––––––
obj..       Benefit =E=  Capacity + Arbitraje + Hidrogeno;
r1..        Capacity =e= -kappaP1*pbmax('t19')-kappaP2*pbmax('t20')-kappaP3*pbmax('t10')-kappaP4*pbmax('t11')-kappaP5*pbmax('t24')-kappaP6*pbmax('t1');;
r2..        Arbitraje =e= 365*(SUM(t,  lam(t)*Ps(t)- (lam(t)+tariff(t))*Pb(t)));
r3..        Hidrogeno =e= 365*(H2_price*H2_total_dia- H2O_price*H2O_total_dia);
*––– Balance de potencia ––––––––––––––––––––––––––––––––––––––––––––––––––
r4(t)..                 Pd(t) + Pb(t) + Ppvmax*Ppvu(t) =E= Pc(t) + Ps(t) + Plmax*Plu(t) + P_E(t) ;
*––– Dinámica del SOC ––––––––––––––––––––––––––––––––––––––––––––––––––––
r5..                    SOC('t1') =E= SOC0 + Pc('t1')*eff_c - Pd('t1')/eff_d ;
r6(t)$(ORD(t)>1)..      SOC(t) =E= SOC(t-1) + Pc(t)*eff_c - Pd(t)/eff_d ;
*––– Exclusión carga-descarga / import-export ––––––––––––––––––––––––––––
r7(t)..                 Pc(t) =L= R_c*C*w1(t) ;
r8(t)..                 Pd(t) =L= R_d*C*(1-w1(t)) ;
r9(t)..                 Pb(t) =L= Pmax*w3(t) ;
r10(t)..                Ps(t) =L= Pmax*(1-w3(t)) ;
*––– Electrolizador ––––––––––––––––––––––––––––––––––––––––––––––––––––––
r11(t)..                aE(t)+bE(t)+csE(t) =E= 1 ;
r12..                   aE('t1')=E= 1 ;
r13..                   bE('t1')=E= 0 ;
r14..                   csE('t1')=E= 0 ;
r15..                   rh('t1')=E= 0 ;
r16(t)..                rh(t) =L= bE(t) ;
r17(t)..                rh(t) =G= CMP*bE(t) ;
r18(t)..                P_E_prod(t) =E= PH2_prod*rh(t) ;
r19(t)..                P_E(t) =E= P_E_prod(t) + PH2_sb*csE(t) + PH2_idle*aE(t) ;
r20(t)..                P_E(t) =L= SH2 ;
r21(t)..                H2_prod(t)*eta_H2 =E= P_E_prod(t) ;
r22(t)..                H2_prod(t) =L=  H2_max_hora;
r23..                   H2_total_dia =E= SUM(t, H2_prod(t)) ;
r24..                   H2_total_anual =E= H2_total_dia*365 ;
r25..                   H2O_total_dia =E= eta_H2O*H2_total_dia;
r26..                   H2O_total_anual =E= 365*H2O_total_dia;
* arranques y transiciones
r27(t)$(ORD(t)>1)..     dE(t) =L= bE(t) ;
r28(t)$(ORD(t)>1)..     dE(t) =L= aE(t-1) ;
r29(t)$(ORD(t)>1)..     dE(t) =G= bE(t)+aE(t-1)-1 ;
r30(t)$(ORD(t)>1)..     fE(t) =L= bE(t) ;
r31(t)$(ORD(t)>1)..     fE(t) =L= csE(t-1) ;
r32(t)$(ORD(t)>1)..     fE(t) =G= bE(t)+csE(t-1)-1 ;
r33..                   SUM(t$(ORD(t)>1), dE(t)) =L= IA ;
r34..                   CashFlow =e= Capacity+Arbitraje+Hidrogeno-Base;
r35..                   Investment =e=    CAPEXpv*Ppvmax+CAPEX_BESS*C+CAPEX_BESS_inverter*C*R_c+CAPEX_H2*SH2;
r36..                   npv=e=CashFlow/crf-Investment;
r37..                   Base =e=365*sum((t), -(data(t,'lambda')+data(t,'psi'))* Plmax*data(t,'Plu'))+Capacity0;
r38(t)..                data(t,'Pbmax') =g= Pb(t);
r39..                   Wload=e=365*sum((t),data(t,'Plu'))*Plmax;
r40..                   Wpvtot=e=365*sum((t),data(t,'Ppvu'))*Ppvmax;
r41..                   Wimport=e= 365*sum((t),Pb(t));
r42..                   Wexport=e= 365*sum((t),Ps(t));
r43..                   WcargaBESS =e= 365*sum((t),Pc(t));
r44..                   WdescargaBESS =e= 365*sum((t),Pd(t));
r45..                   Welectrolizador =e= 365*sum((t),P_E(t));
option mip=gurobi minlp=gurobi, miqcp=gurobi;
*option mip=lindo;
*option mip=clpex;
*---------------------------------------------------------------------------
* 6  MODELO Y SOLUCIÓN
*---------------------------------------------------------------------------
MODEL AGPE_ES_H2 / ALL / ;
SOLVE AGPE_ES_H2 USING MIP MAXIMIZING Benefit;

EXECUTE_UNLOAD 'Results_M1_5_E1e.gdx' ;
