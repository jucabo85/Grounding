from math import sqrt
import numpy as np

def surface_correction(ro, ros, depth):
    #calculate the surface correction factor
    Cs=1-(0.09*(1-ro/ros)/(2*depth+0.09))
    return Cs

def Etouch(ros,Cs, ts,Rb=1000, weight=50):
    #calculate the touch voltage
    if weight==50:
        s=0.116
    elif weight==70:
        s=0.157
    else:
        raise ValueError("Unsupported weight value. Supported values are 50 kg and 70 kg.")

    return (Rb+1.5*Cs*ros)*s/sqrt(ts)

def Estep(ros,Cs, ts,Rb=1000, weight=50):
    #calculate the touch voltage
    if weight==50:
        s=0.116
    elif weight==70:
        s=0.157
    else:
        raise ValueError("Unsupported weight value. Supported values are 50 kg and 70 kg.")

    return (Rb+6*Cs*ros)*s/sqrt(ts)

if __name__ == '__main__':

    #Using values from IEEE 80 appendix B
    ro=400                      # Ohm-m
    ros=2500                    # Ohm-m
    depth_crushed_rock=0.102    # 4 inches
    fault_duration=0.5          # seconds
    person_weight=70            # kg
    short_circuit=20            # kA
    split_factor=1              # unitless

    Cs=np.round(surface_correction(ro,ros,depth_crushed_rock),3)
    Est=Estep(ros,Cs,fault_duration,weight=person_weight)
    Eto=Etouch(ros,Cs,fault_duration,weight=person_weight)
    print("Estep=",Est)
    print("Etouch=",Eto)

    print("Cs=",Cs)