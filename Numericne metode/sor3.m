function [x]  = sor3(M, b, x_0, omega, nat, maxit)
    format long;
    D=M(:,1);%diagonala
    L=M(:,2);%diagonala pod diagonalo
    U=M(:,3);%diagonala nad diagonalo
    n = length(D);%dolzina diagonale
    x=zeros(n,1);
    a=(D-omega*L);
    tol=10^-nat;    
    for i=1:maxit
        x = a\(((1-omega)*D + omega*U)*x_0) + omega*(a\b);
        if norm(x-x_0)<tol
            break;
        end
        x_0=x;
    end
end