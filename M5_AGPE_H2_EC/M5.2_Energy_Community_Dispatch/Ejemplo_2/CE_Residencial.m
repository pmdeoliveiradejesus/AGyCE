%  Simulador de CE Residencial de n usuarios/fronteras
clear all
close all
clc
% En este emplo se dispone de una comunidad enerética
% de 5 usuarios residenciales
% cada uno con generación PV propia
% con un parque de generación comunitario de 50kWp
Wload=[500 600 400 300 450 0] ;%kWh/mes
Ppvinst=[0 0 0 0 0 10] ;%kWp
CAPEXpv=770;%USD/kWp
Ppvu=[0.000
0.000
0.000
0.000
0.000
0.000
0.047
0.200
0.372
0.512
0.605
0.645
0.627
0.569
0.473
0.337
0.189
0.044
0.000
0.000
0.000
0.000
0.000
0.000];% Radiación solar media anual en COLOMBIA como fracción de 1000W/m2
PLu=[0.45
0.40
0.39
0.39
0.50
0.60
0.57
0.59
0.60
0.61
0.62
0.60
0.50
0.45
0.45
0.46
0.53
0.60
0.95
1.00
0.90
0.75
0.55
0.45];% Curva residencial Típica
LoadFactor=mean(PLu)/max(PLu);
PLmax=Wload./(720*LoadFactor);
PL=PLu.*PLmax;
QL=0.4*PL;%Potencia reactiva kvar
CUmedio2024=959.06;%COP/kWh
SpotMedio2024=617.7571;%COP/kWh;
TRM=4000;%COP/kWh en 2024
Ppv=Ppvinst.*Ppvu;%kW
Pnet=PL-Ppv;%kW
Imp=zeros(1,length(Wload));
Exp=zeros(1,length(Wload));
Exc1=zeros(1,length(Wload));
Exc2=zeros(1,length(Wload));
Imp=365*sum(PL);
Expo=365*sum(Ppv);
for k=1:length(Wload)
if Imp(k) > Expo(k)
    Exc1(k) = Expo(k);
    Exc2(k) = 0;
else
    Exc1(k) = Imp(k);
    Exc2(k) = Expo(k)-Imp(k);   
end
end
Parte1 = (Exc1-Imp)*CUmedio2024/TRM;%USD/año
Cv=132.98/TRM;%USD/kWh (Componente de Comercialización)
Parte2=Exc1*Cv;%USD/año
Parte3 = 0; %AGPE < 100kW
Cm=SpotMedio2024/TRM;
Parte4= Cm*Exc2;%USD/año
 VE=(Parte1+Parte2+Parte3+Parte4);
VET=sum(VE);
Crespaldo=2.5;%USD/kW
Pdeclarada=max(abs(Ppv));
if sum(Ppvinst) >100
PagoRespaldo=-12*Pdeclarada*Crespaldo;%CREG 015 2018 Capitulo 10
else
PagoRespaldo=0;
end
%% Potencia Reactiva
D=167.42/TRM;
M=1;%M=1, solo los primeros 2 años, despues habra resolución especifica
Qexce=zeros(24,length(Wload));
PagoQ=zeros(24,length(Wload));
for k=1:length(Wload)
for t=1:24
if cos(atan(QL(t,k)/(Pnet(t,k)))) < 0.9
Qexce(t,k)=QL(t,k)-sqrt((Pnet(t,k)/0.9)^2-Pnet(t,k)^2);
PagoQ(t,k)=Qexce(t,k)*D*M;
     end
end
end
PagoQporFrontera=sum(PagoQ);
PagoQtotal=-365*sum(sum(PagoQ));
TotalFactura=PagoRespaldo+VET+PagoQtotal;
PagoSinPV=-365*sum(sum(PL))*CUmedio2024/TRM;%USD/año
Ahorro=TotalFactura-PagoSinPV;
%% Indices de bondad finaciera del proyecto de CE 
Io=sum(Ppvinst)*CAPEXpv;% CAPEX USD
Rate=0.05;%Discount rate %
S=Ahorro; %OPEX
n=20; %Lifetime
CashFlow=ones(1,n)*S;
NPV = -Io+pvfix(Rate,n,S);
TIR=irr([-Io,CashFlow])*100;
BCratio=pvfix(Rate,n,S)/Io;
% Define input parameters
PV = -Io; % Present Value (initial loan or investment amount)
PMT = S;  % Payment made each period (e.g., monthly)
rate = Rate; % Interest rate per period (annual interest rate divided by 12 for monthly)
FV = 0;     % Future Value (desired amount at the end of the periods, typically 0 for loans)
% Calculate the number of periods (NPER)
if rate == 0
    % Special case where interest rate is 0
    NPER = PV / PMT;
else
    % General formula for NPER
    NPER = log((PMT - rate * FV) / (PMT + rate * PV)) / log(1 + rate);
end
NPER;
FacturaTotalAnualUsuario_sinPV=-(Imp)*CUmedio2024/TRM;%USD/año
FacturaTotalAnualUsuarios_sinPV=-sum(Imp)*CUmedio2024/TRM;%USD/año
FacturaTotalAnualUsuario_conPV=VE;
FacturaTotalAnualUsuarios_conPV=VET;

AhorroIndiv =100*(1-FacturaTotalAnualUsuario_conPV./FacturaTotalAnualUsuario_sinPV);
Ahorro =100*(1-FacturaTotalAnualUsuarios_conPV/FacturaTotalAnualUsuarios_sinPV);

% 
%% Distribución de excedentes (Ventas de energía por Usuario una vez amortizado el proyecto)
for k=1:length(Wload)-1
PDE(k)=1/5;
Vex(k)=PDE(k)*VET;
end
Vex(6)=0;

 %% Facturación de energía a lo interno de la comunidad para cada usuario
 for k=1:5
 FacturaAnualUsuario_sinPV(k)=-Imp(k)*CUmedio2024/TRM;%USD/año
 FacturaAnualUsuario_conPV(k)=Vex(k);%USD/año
 end
% 
% 
% %% Resultado Global de la CE
 Balance=sum(FacturaAnualUsuario_conPV)-sum(FacturaAnualUsuario_sinPV(k));%USD/año
% Energia=sum(Imp);
CostoMedioEnergia=-sum(FacturaAnualUsuario_sinPV)/(365*sum(sum(PL))) %USD/kWh
 CostoMedioEnergiaProyecto=-sum(FacturaAnualUsuario_conPV)/(365*sum(sum(PL))) %USD/kWh
 ReduccionTarifa= 100-CostoMedioEnergiaProyecto*100/(CUmedio2024/TRM) %pct
TIR % pct
NPER  %años
CAPEXtotal=sum(Ppvinst)*CAPEXpv; %USD


