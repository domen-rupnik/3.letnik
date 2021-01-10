function [M,xM,p]=maksimum(d,x0)

p=dolocipolinom(0,0,1,d);%izracunamo polinom
d=[0 0 0 0];
for i=1:3%izracun odvoda
    d(i+1)=p(i)*(4-i);
end
dd=[0 0 0 0];
for i=1:3%izracun odvoda odvoda
    dd(i+1)=d(i)*(4-i);
end
%definiramo polinom
polinom=@(x) p(1)*x^3+p(2)*x^2+p(3)*x+p(4);
%odvod polinoma
dpolinom=@(x) d(1)*x^3+d(2)*x^2+d(3)*x+d(4);
%odvod odvoda
ddpolinom=@(x)dd(1)*x^3+dd(2)*x^2+dd(3)*x+dd(4);
k=8;
while k>0
    y=dpolinom(x0);
    dy=ddpolinom(x0);
    x=x0-dy\y;
    k=k-1;
    x0=x;
    
end
M=polinom(x0);
xM=[x0 polinom(x0)];
