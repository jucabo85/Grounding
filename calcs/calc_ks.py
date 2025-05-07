import numpy as np

def k1(ratio,h, A):
    # Difining known points to interpolation
    h_values=[0, 1/10*np.sqrt(A), 1/6*np.sqrt(A)]
    k1_values=[-0.04*ratio+1.41,-0.05*ratio+1.20,-0.05*ratio+1.13]

    # Handle vector input for h
    if isinstance(h, (list, np.ndarray)):
        return [k1(ratio, hi, A) for hi in h]

    # calculation for values at zero or below (it can't happen below)
    if h<=h_values[0]:
        return float(k1_values[0])
    
    #Extrapolation for the values beyond the known h
    elif h>=h_values[-1]:
        slope=(k1_values[-1]-k1_values[-2])/(h_values[-1]-h_values[-2])
        return float(k1_values[-1]+slope*(h-h_values[-1]))
    
    else:
        for i in range(len(h_values)-1):
            if h_values[i]<=h<=h_values[i+1]:
                slope=(k1_values[i+1]-k1_values[i])/(h_values[i+1]-h_values[i])
                return float(k1_values[i]+slope*(h-h_values[i]))
            
def k2(ratio,h, A):
    # Difining known points to interpolation
    h_values=[0, 1/10*np.sqrt(A), 1/6*np.sqrt(A)]
    k2_values=[0.15*ratio+5.5,0.1*ratio+4.68,-0.05*ratio+4.4]

    # Handle vector input for h
    if isinstance(h, (list, np.ndarray)):
        return [k2(ratio, hi, A) for hi in h]

    # calculation for values at zero or below (it can't happen below)
    if h<=h_values[0]:
        return float(k2_values[0])
    
    #Extrapolation for the values beyond the known h
    elif h>=h_values[-1]:
        slope=(k2_values[-1]-k2_values[-2])/(h_values[-1]-h_values[-2])
        return float(k2_values[-1]+slope*(h-h_values[-1]))
    
    else:
        for i in range(len(h_values)-1):
            if h_values[i]<=h<=h_values[i+1]:
                slope=(k2_values[i+1]-k2_values[i])/(h_values[i+1]-h_values[i])
                return float(k2_values[i]+slope*(h-h_values[i]))

def calc_kii(n_calc,location_rods="non_perimeter"):
    if n_calc==0 or location_rods=="non_perimeter":
        # print("N_calc_type",type(n_calc))
        Kii=1/((2*n_calc)**(2/n_calc))
    else:
        Kii=1
    return Kii

def kh(h,h0=1):
    return np.sqrt(1+h/h0)

def na(self):
        return 2 * self.Lc / self.Lp

def nb(self):
        return np.sqrt(self.Lp / (4 * np.sqrt(self.A)))

def nc(self):
        return np.power((self.Lx * self.Ly) / self.A, 0.7 * self.A / (self.Lx * self.Ly))

def nd(self):
        return self.Dm / np.sqrt(self.Lx**2 + self.Ly**2)
