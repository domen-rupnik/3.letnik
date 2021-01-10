function p=dolocipolinom(x1,x2,dx1,dx2)
b=[x1;x2;dx1;dx2];
iA=[2 -2 1 1;-3 3 -2 -1;0 0 1 0;1 0 0 0];
p=iA*b;