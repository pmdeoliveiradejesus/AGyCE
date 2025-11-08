clc
clear all
close all
% Irradiance in Barranquilla Colombia
SolarDB;%Call the database
%DB(:,1) year
%DB(:,2) month
%DB(:,3) day
%DB(:,4) hour
%DB(:,6) GHI w/m2
%DB(:,7) DHI w/m2
%DB(:,8) DNI w/m2
n=length(DB(:,1));
Irr=zeros(24,1);
for h=1:24
for k=1:n
%if DB(k,1) == 2022
    if DB(k,4) == h-1
         Irr(h,1)= Irr(h,1)+DB(k,6); 
%end
end
end
end
Irr/(365*5)



