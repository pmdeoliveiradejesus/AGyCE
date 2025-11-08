% M1_4_E3e PV Solar + Industria (España, 24h)
clear all
clc
close all
database;
Plumax=231.24136986301;
Ppvmax=569;
Pneto=Ppvmax*Ppvu-PLu*Plumax;
compras=zeros(1,24);
ventas=zeros(1,24);
for k=1:24
if Pneto(k) < 0
compras(k)=(lambda(k)+psi(k))*Pneto(k); 
importa(k)=Pneto(k);
else
ventas(k)=(lambda(k)*Pneto(k));
exporta(k)=Pneto(k);
end
end
Beneficio=ventas+compras;
Ventas=365*sum(ventas) %kWh/año
Compras=365*sum(compras) %kWh/año
ConsumoIndustria=365*sum(PLu*Plumax)%kWh/año
ProduccionPV=365*sum(Ppvmax*Ppvu)%kWh/año
Imp=365*sum(importa) %Eur/año
Exp=365*sum(importa) %Eur/año
Lucro=365*sum(Beneficio)-kappa'*Pbmax_PV%Eur/año
base_noPV=-365*sum(PLu.*(lambda+psi)*Plumax);%Eur/año
cashflow=365*sum(Beneficio)-base_noPV-kappa'*Pbmax_PV+kappa'*Pbmax_noPV%Eur/año
% % Análisis Financiero
% Io=569*700;% CAPEX EUR
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
