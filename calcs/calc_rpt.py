

import numpy as np
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calcs.plotting_ks import plotting_ks
from calcs.calc_ks import k1,k2

def Resistance(ro,A ,Lc, depth, diameter, nrods, rod_length, rod_diam,side1,side2,side3,side4, D=0,shape="rectangle",case="Schwarz"):
    
    if D!=0:
        if shape=="L":
            Lc=(side1/D+1)*side2+ (side2/D+1)*side1 +(side3/D+1)*side4 +(side4/D+1)*side3 -side2
        elif shape=="rectangle":
            Lc=(side1/D+1)*side2+ (side2/D+1)*side1 

    #Calculating areas depending on the shape of the grid
    if shape=="L":
        A=side1*side2+side3*side4
    elif shape=="rectangle":
        A=side1*side2
    elif shape=="imported":
        pass
    else: 
        return "Non-supported shape"
    
    #Calculating grid ratios
    if side1 / side2 < 1:
        ratio = side2 / side1
    else:
        ratio = side1 / side2
        
    #calculating different cases
    if case=="simplified1":
        return ro/4*np.sqrt(np.pi/A)
    elif case=="simplified2":
        Lt=Lc+nrods*rod_length
        return ro/4*np.sqrt(np.pi/A)+ro/Lt
    elif case=="Sverak":
        Lt=Lc+nrods*rod_length
        return ro*(1/Lt+(1+1/(1+depth*np.sqrt(20/A)))/np.sqrt(20*A))
    elif case=="Schwarz":
        ap=np.sqrt(diameter*depth)
        K1=k1(ratio,depth,A)
        K2=k2(ratio,depth,A)
        if nrods!=0:
            R1 = (ro/(np.pi*Lc))*(np.log(2*Lc/ap)+K1*Lc/np.sqrt(A)-K2)
            R2= (ro/(2*np.pi*nrods*rod_length))*(np.log(4*rod_length/rod_diam/2)-1+(2*K1*rod_length)*((np.sqrt(nrods)-1)**2)/(np.sqrt(A)))
            Rm=(ro/(np.pi*Lc))*(np.log(2*Lc/rod_length)+(K1*Lc)/np.sqrt(A)-K2+1)
            Rpt=(R1*R2-Rm**2)/(R1+R2-2*Rm)
            # print("R1=",R1)
            # print("R2=",R2)
            # print("RM=",Rm)
        elif nrods==0:
            Rpt = (ro/(np.pi*Lt))*(np.log(2*Lt/ap)+K1*Lt/np.sqrt(A)-K2)

        return Rpt


if __name__ == '__main__':

    #Testing the Ks functions first
    ratio=1
    A=10
    depth_vector=[0,(1/10*np.sqrt(A)),(1/6*np.sqrt(A))]
    new_depths=[0.2, 0.4, 0.6, 0.8, 1]
    depth_vector.extend(new_depths)

    K_one=k1(ratio,depth_vector,A)
    K_dos=k2(ratio,depth_vector,A)

    print("K_one=",K_one)
    print("K_dos=",K_dos) 

    #replicating Ks plots:
    # plotting_ks((0,8),depth_vector,A)

    # Data to test the Rpt function using IEEE 80 Appendix B 
    ro=400
    side1=70
    side2=70
    D=7
    A=side1*side2
    Lt=(side1/D+1)*side1+(side2/D+1)*side2
    depth=0.5
    diameter_cond=1/100
    nrods=20
    rod_length=7.5
    rod_diam=5/8*25.4/1000

    print("Lt",Lt)

    # Example 1. Appendix B
    Rpt_Ex1=Resistance(ro,A,Lt,depth,diameter_cond,0,rod_length,rod_diam,side1, side2,0, 0,D,"rectangle", case="Sverak")
    print("Rpt-Sverak-1", Rpt_Ex1)

    Rpt_Ex1_Schwarz=Resistance(ro,A,Lt,depth,diameter_cond,0,rod_length,rod_diam,side1, side2,0, 0,D,"rectangle", case="Schwarz")
    print("Rpt-Schwarz-1", Rpt_Ex1_Schwarz)

    # Example 2. Appendix B
    Rpt_Ex2=Resistance(ro,A,Lt,depth,diameter_cond,nrods,rod_length,rod_diam,side1,side2,0,0,D,case="Sverak")
    print("Rpt-Sverak-2", Rpt_Ex2)

    Rpt_Ex2_Schwarz=Resistance(ro,A,Lt,depth,diameter_cond,nrods,rod_length,rod_diam,side1, side2,0, 0,D,"rectangle", case="Schwarz")
    print("Rpt-Schwarz-2", Rpt_Ex2_Schwarz)

    # Midifying for Example 3
    side1=63
    side2=84
    A=side1*side2
    Lt=(side1/D+1)*side2+(side2/D+1)*side1
    nrods=38
    rod_length=10
    # print("Lt",Lt)
    # print("A", A)

    # Example 3. Appendix B
    Rpt_Ex3=Resistance(ro,A,Lt,depth,diameter_cond,nrods,rod_length,rod_diam,side1,side2, 0, 0,D, case="Sverak")
    print("Rpt-Sverak-3", Rpt_Ex3)

    Rpt_Ex3_Schwarz=Resistance(ro,A,Lt,depth,diameter_cond,nrods,rod_length,rod_diam,side1, side2,0, 0,D,"rectangle", case="Schwarz")
    print("Rpt-Schwarz-3", Rpt_Ex3_Schwarz)

    # Example 4. Appendix B

    side1=70
    side2=35
    side3=side1
    side4=side2
    nrods=24
    rod_length=7.5
    Lt1=(side1/D+1)*side2
    Lt2=(side2/D+1)*side1
    Lt3=(side3/D+1)*side4
    Lt4=(side4/D+1)*side3
    Lt=Lt1+Lt2+Lt3+Lt4-side2
    # print("Lt1 Lt2 Lt3 Lt4 Lt Ltr",Lt1, Lt2, Lt3, Lt4, Lt, Lt+nrods*rod_length)
    # print("A4",side1*side2+side3*side4)


    Rpt_Ex4=Rpt(ro,A,Lt,depth,diameter_cond,nrods,rod_length,rod_diam,side1,side2, side3, side4, D,shape="L",case="Sverak")
    print("Rpt-Sverak-4", Rpt_Ex4)

    Rpt_Ex4_Schwarz=Rpt(ro,A,Lt,depth,diameter_cond,nrods,rod_length,rod_diam,side1, side2,side3, side4,D,"L", case="Schwarz")
    print("Rpt-Schwarz-4", Rpt_Ex4_Schwarz)
    