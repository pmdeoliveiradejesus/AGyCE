clear all
clc
%Bases
vb=220;%V
sb=6000;%VA
zb=vb^2/sb;%ohms base impedance
ZL=(1+0.4j)/zb;% impedance pu
PG=6000/sb; % power load pu
v1=1;%pu slack bus
% initialize Gauss
v2=v1;
for i=1:10
I1=conj(PG/v2); %Injected current
J01=-I1; %pu KCL
v2=v1-J01*ZL; %pu LVL
end
mv1=abs(v2)
%solution
percentageVDrise=100*(mv1-1)

