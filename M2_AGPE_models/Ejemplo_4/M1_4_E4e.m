% M1_4_E4e PV Solar + Industria (Colombia, 24h)
clear all
clc
close all
database;
Plumax=231.24136986301;%kW
Ppvmax=569;%kW
kappa=5;%USD/kW-mes
Pbmax_PV=Ppvmax;%kW contratados (respaldo)
Pneto=Ppvmax*Ppvu-PLu*Plumax;
compras=zeros(1,24);
ventas=zeros(1,24);
for k=1:24
if Pneto(k) < 0
%compras(k)=(lambda(k)+psi(k))*Pneto(k); 
importa(k)=Pneto(k);
else
%ventas(k)=(lambda(k)*Pneto(k));
exporta(k)=Pneto(k);
end
end
Imp=-365*sum(importa);
Exp=365*sum(exporta);
if Exp < Imp
    Exc2=0;
    Exc1=Exp;
else
    Exc1=Imp;
    Exc2=Exp-Imp;
end
Beneficio=(Exc1-Imp)*CU-Exc1*(T+PR+D+Cv+R)+Exc2*Cm;
ConsumoIndustria=365*sum(PLu*Plumax)%kWh/año
ProduccionPV=365*sum(Ppvmax*Ppvu)%kWh/año
Lucro=365*sum(Beneficio)-12*kappa*Pbmax_PV%Eur/año
base_noPV=-365*sum(PLu.*(CU)*Plumax);%Eur/año
PagoReactiva_noPV=-24942.37;
cashflow=sum(Beneficio)-base_noPV-12*kappa'*Pbmax_PV-PagoReactiva_noPV%Eur/año
% % Análisis Financiero
% Io=569*770;% CAPEX USD
% Rate=0.05;%Discount rate %
% S=cashflow; %OPEX EUR
% n=20; %Lifetime
% CashFlow=ones(1,n)*S;
% NPV = -Io+pvfix(Rate,n,S)
% TIR=irr([-Io,CashFlow])*100
% BCratio=pvfix(Rate,n,S)/Io
% % Define input parameters
% PV = -Io; % Present Value (initial loan or investment amount)
% PMT = S;  % Payment made each period (e.g., monthly)
% rate = Rate; % Interest rate per period (annual interest rate divided by 12 for monthly)
% FV = 0;     % Future Value (desired amount at the end of the periods, typically 0 for loans)
% % Calculate the number of periods (NPER)
% if rate == 0
%     % Special case where interest rate is 0
%     NPER = PV / PMT;
% else
%     % General formula for NPER
%     NPER = log((PMT - rate * FV) / (PMT + rate * PV)) / log(1 + rate);
% end
% NPER
% 
