import numpy as np
import matplotlib.pyplot as plt

from calcs.calc_ks import kii,kh

from plotting_ks import plotting_kii

def Em(ro, Km, Ki, Ig, Lm):
    return ro*Km*Ki*Ig/Lm

def Es(ro, Ks, Ki, Ig, Ls):
    return ro*Ks*Ki*Ig/Ls

def Lm(Lc,Lr,Lx, Ly, rod_length,location_rods="non_perimeter"):
    if location_rods=="non_perimeter":
        return Lc+Lr
    elif location_rods=="perimeter":
        return Lc+Lr*(1.22*rod_length/np.hypotenuse(Lx,Ly))


def na(Lc,Lp):
    return 2*Lc/Lp

def nb(Lp,A):
    return np.sqrt(Lp/(4*np.sqrt(A)))

def nc(Lx,Ly,A):
    return np.power((Lx*Ly)/A,0.7*A/(Lx*Ly))

def nd(Dm, Lx, Ly):
    return Dm/np.sqrt(Lx**2+Ly**2)

def ncalc(na,nb,nc,nd):
    return na*nb*nc*nd

def ki(n_calc):
    return n_calc*0.148+0.644

def Km(D, h, d, n_calc,depth,location_rods):
    km=(1/(2*np.pi))*(np.log((D**2)/(16*h*d)+((D+2*h)**2)/(8*D*d)-h/(4*d))+(kii(n_calc,location_rods)/kh(depth)*np.log(8/(np.pi*(2*n_calc-1)))))
    return km

def Km1(D, h, d, n_calc,depth,location_rods):
    km=(1/(2*np.pi))*np.log((D**2)/(16*h*d)+((D+2*h)**2)/(8*D*d)-h/(4*d))
    return km

def Km2(D, h, d, n_calc,depth,location_rods):
    km=(1/(2*np.pi))*(kii(n_calc,location_rods)/kh(depth)*np.log(8/(np.pi*((2*n_calc)-1))))
    return km

if __name__== "__main__":
    # plotting_kii() #Ploting kii to check sensibility

    # Example 1. Appendix B
    side1=70
    side2=70
    D=7
    A=side1*side2
    L_c=(side1/D+1)*side1+(side2/D+1)*side2
    Lp=2*side1+2*side2
    depth=0.5
    d=1/100
    Lx=side1
    Ly=side2
    Dm=np.sqrt(Lx**2+Ly**2)
    print("Lt=",L_c)
    print("Lp=",L_c)
    n_a=na(L_c,Lp)
    n_b=nb(Lp,A)
    n_c=nc(Lx,Ly,A)
    n_d=nd(Dm,Lx,Ly)
    print("n_a=",n_a)
    print("n_b=",n_b)
    print("n_c=",n_c)
    print("n_d=",n_d)
    ncal=ncalc(n_a,n_b,n_c,n_d)
    ki_value=ki(ncal)
    print("ki=",ki_value)
    k_h=kh(depth)
    print("k_h=",k_h)
    k_ii=kii(ncal)
    print("k_ii=",k_ii)
    k_m1=Km1(D, depth, d, ncal,depth,"non_perimeter")
    print("k_m1=",k_m1)
    k_m2_step1 = kii(ncal, "non_perimeter") / kh(depth)
    k_m2_step2 = np.log(8 / (np.pi * ((2 * ncal) - 1)))
    k_m2 = (1 / (2 * np.pi)) * (k_m2_step1 * k_m2_step2)
    print("k_m2_step1=", k_m2_step1)
    print("k_m2_step2=", k_m2_step2)
    print("k_m2=",k_m2)
    k_m=Km(D, depth, d, ncal,depth,"non_perimeter")
    print("k_m=",k_m)
    L_m=Lm(L_c,0, Lx, Ly, 0,"non_perimeter")
    print("L_m=",L_m)
    E_m=Em(400, k_m, ki_value, 1908, L_m)
    print("E_m=",E_m)



    
    print("ncalc=",ncal)