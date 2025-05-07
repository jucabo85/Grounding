import numpy as np
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calcs.calc_rpt import Resistance

class GroundingGrid:
    def __init__(self, ro, cable_depth, cable_diameter, num_rods, rod_length, rod_diameter,
                 case, location_rods, D, shape, side1, side2, side3, side4, A, Lc, Lp, Dm, Lx, Ly):
        self.ro = ro  # Soil resistivity (Ohm-m)
        self.cable_depth = cable_depth  # Depth of the cable (meters)
        self.cable_diameter = cable_diameter  # Diameter of the cable (meters)
        self.num_rods = num_rods  # Number of rods
        self.rod_length = rod_length  # Length of each rod (meters)
        self.rod_diameter = rod_diameter  # Diameter of each rod (meters)
        self.case = case  # Grounding resistance model
        self.location_rods = location_rods  # Location of rods
        self.D = D  # Maximum separation between rods
        self.shape = shape  # Shape of the grid
        self.side1 = side1  # Side 1 length
        self.side2 = side2  # Side 2 length
        self.side3 = side3  # Side 3 length
        self.side4 = side4  # Side 4 length
        self.A = A  # Area of the grid
        self.Lc = Lc  # Total length of conductors
        self.Lp = Lp  # Perimeter of the grid
        self.Dm = Dm  # Maximum distance within the grid
        self.Lx = Lx  # Maximum length in the X direction
        self.Ly = Ly  # Maximum length in the Y direction
        self.LR= self.num_rods*self.rod_length # Total length of rods
        self.Lt = self.Lc + self.LR  # Total length of conductors including rods
        self.Calc_Resistance()
        self.calc_n()  # Calculate the n factor
        self.calc_kii()  # Calculate the kii factor
        self.calc_kh()  # Calculate the kh factor
        self.calc_Km()  # Calculate the Km factor
        self.calc_Ki()  # Calculate the Ki factor
        self.calc_Lm()  # Calculate the Lm factor
        self.calc_Ks()  # Calculate the Ks factor
        self.calc_Ls()  # Calculate the Ls factor

    def Calc_Resistance(self):
        """
        Calculate the grounding resistance (Ohms).
        """
        self.Rpt=Resistance(
            ro=self.ro,
            A=self.A,
            Lc=self.Lc,
            depth=self.cable_depth,
            diameter=self.cable_diameter,
            nrods=self.num_rods,
            rod_length=self.rod_length,
            rod_diam=self.rod_diameter,
            side1=self.side1,
            side2=self.side2,
            side3=self.side3,
            side4=self.side4,
            D=self.D,
            shape=self.shape,
            case=self.case
        )

    def Em(self, current):
        """
        Calculate the touch potential (Volts).
        """
        return (self.ro*current*self.km*self.ki)/self.Lm

    def Es(self, current):
        """
        Calculate the step potential (Volts).
        """
        return (self.ro*current*self.ks*self.ki)/self.Ls
    
    def calc_kii(self):
        """
        Calculate the kii factor based on the number of rods.
        """
        if self.location_rods=="perimeter":
            self.kii=1
        elif  self.location_rods!="perimeter" or self.num_rods==0:
            self.kii= 1 / ((2 * self.n) ** (2 / self.n))
    
    def calc_kh(self,h0=1):
        """
        Calculate the kh factor based on the depth of the cable.
        """
        self.kh = (1 + self.cable_depth / h0) ** 0.5

    def calc_n(self):
        """
        Calculate the n factor based on the grid parameters.
        """
        self.na=2*self.Lc/self.Lp
        self.nb=np.sqrt(self.Lp/(4*np.sqrt(self.A)))
        self.nc=(self.Lx*self.Ly/self.A)**(0.7*self.A/(self.Lx*self.Ly))
        self.nd=self.Dm/np.hypot(self.Lx,self.Ly)
        self.n=self.na*self.nb*self.nc*self.nd

    def calc_Km(self):
        """
        Calculate the Km factor based on the grid parameters.
        """
        self.km_first=self.D**2/(16*self.cable_depth*self.cable_diameter)
        self.km_second=((self.D + 2*self.cable_depth)**2)/(8*self.cable_diameter*self.D)
        self.km_third=-self.cable_depth/(4*self.cable_diameter)
        self.km_fourth=self.kii/self.kh
        self.km_sixth=8/(np.pi*((2*self.n)-1))
        self.km_fifth=np.log(self.km_sixth)
        self.km_seventh=np.log(self.km_first+self.km_second+self.km_third)
        self.km=(1/(2*np.pi))*(self.km_seventh+self.km_fourth*self.km_fifth)

    def calc_Ki(self):
        """
        Calculate the Ki factor based on the grid parameters.
        """
        self.ki = 0.644+0.148*self.n

    def calc_Lm(self):
        """
        Calculate the Lm factor based on the grid parameters.
        """
        if self.location_rods!="perimeter" or self.num_rods==0:
            self.Lm=self.Lc + self.LR
        elif self.location_rods=="perimeter":
            self.Lm=self.Lc+(self.LR)*(1.55+1.22*(self.rod_length/np.hypot(self.Lx,self.Ly)))

    def calc_Ks(self):
        """
        Calculate the Ks factor based on the grid parameters.
        """
        self.ks = (1/np.pi)*(1/(2*self.cable_depth)+1/(self.D+self.cable_depth)+(1-0.5**(self.n-2))/self.D)

    def calc_Ls(self):
        """
        Calculate the Ls factor based on the grid parameters.
        """
        self.Ls=0.75*self.Lc+0.85*self.LR

    


    
if __name__ == "__main__":
    # Example parameters IEEE B2
    ro = 400  # Soil resistivity (Ohm-m)
    cable_depth = 0.5  # Depth of the cable (meters)
    cable_diameter = 0.01  # Diameter of the cable (meters)
    num_rods = 20  # Number of rods
    rod_length = 7.5  # Length of each rod (meters)
    rod_diameter = 0.02  # Diameter of each rod (meters)
    case = "Sverak"  # Grounding resistance model
    location_rods = "perimeter"  # Location of rods 
    D_sep = 7  # Maximum separation between conductors
    shape = "rectangle"  # Shape of the grid
    side1 = 70  # Side 1 length
    side2 = 70  # Side 2 length
    side3 = 0  # Side 3 length (not used for rectangle)
    side4 = 0  # Side 4 length (not used for rectangle)
    Area = side1 * side2  # Area of the grid
    Lc = (side1 / D_sep + 1) * side2 + (side2 / D_sep+ 1) * side1  # Total length of conductors
    Lp = 2 * (side1 + side2)  # Perimeter of the grid
    Dm = np.hypot(side1,side2)  # Maximum distance within the grid
    Lx = side1  # Maximum length in the X direction
    Ly = side2  # Maximum length in the Y direction
    Ig= 1908 # Fault current thru the grid (Amps)

    # Create a GroundingGrid object
    grid1 = GroundingGrid(ro, cable_depth, cable_diameter, num_rods, rod_length, rod_diameter,
                        case, location_rods, D_sep, shape, side1, side2, side3, side4, Area, Lc, Lp, Dm, Lx, Ly)

    # Calculate grounding resistance
    resistance = grid1.Rpt
    print("Grounding Resistance (Ohms):", resistance)

    print("self.Rpt", grid1.Rpt)
    print("self.Lt", grid1.Lt)
    print("self.Lc", grid1.Lc)
    print("self.kii", grid1.kii)
    print("self.kh", grid1.kh)
    print("self.Dm", grid1.Dm)
    print("self.n", grid1.n)
    print("self.na", grid1.na)
    print("self.nb", grid1.nb)
    print("self.nc", grid1.nc)
    print("self.nd", grid1.nd)
    print("self.km_first", grid1.km_first)
    print("self.km_second", grid1.km_second)
    print("self.km_third", grid1.km_third)
    print("self.km_fourth", grid1.km_fourth)
    print("self.km_fifth", grid1.km_fifth)
    print("self.km_sixth", grid1.km_sixth)
    print("self.km_seventh", grid1.km_seventh)
    print("self.km", grid1.km)
    print("self.ki", grid1.ki)
    print("self.Lm", grid1.Lm)
    print("self.ks", grid1.ks)
    print("self.LR", grid1.LR)
    print("self.Lc", grid1.Lc)
    print("self.Lp", grid1.Lp)
    print("self.Ls", grid1.Ls)

    # Calculate touch potential
    touch_potential = grid1.calc_Em(Ig)
    print("Touch Potential (Volts):", touch_potential)

    # Calculate step potential
    step_potential = grid1.calc_Es(Ig)
    print("Step Potential (Volts):", step_potential)


    # # Example parameters IEEE B1
    # ro = 400  # Soil resistivity (Ohm-m)
    # cable_depth = 0.5  # Depth of the cable (meters)
    # cable_diameter = 0.01  # Diameter of the cable (meters)
    # num_rods = 0  # Number of rods
    # rod_length = 7.5  # Length of each rod (meters)
    # rod_diameter = 0.02  # Diameter of each rod (meters)
    # case = "Sverak"  # Grounding resistance model
    # location_rods = None  # Location of rods (not used in this example)
    # D_sep = 7  # Maximum separation between conductors
    # shape = "rectangle"  # Shape of the grid
    # side1 = 70  # Side 1 length
    # side2 = 70  # Side 2 length
    # side3 = 0  # Side 3 length (not used for rectangle)
    # side4 = 0  # Side 4 length (not used for rectangle)
    # Area = side1 * side2  # Area of the grid
    # Lc = (side1 / D_sep + 1) * side2 + (side2 / D_sep+ 1) * side1  # Total length of conductors
    # Lp = 2 * (side1 + side2)  # Perimeter of the grid
    # Dm = np.hypot(side1,side2)  # Maximum distance within the grid
    # Lx = side1  # Maximum length in the X direction
    # Ly = side2  # Maximum length in the Y direction
    # Ig= 1908 # Fault current thru the grid (Amps)

    # # Create a GroundingGrid object
    # grid1 = GroundingGrid(ro, cable_depth, cable_diameter, num_rods, rod_length, rod_diameter,
    #                     case, location_rods, D_sep, shape, side1, side2, side3, side4, Area, Lc, Lp, Dm, Lx, Ly)

    # # Calculate grounding resistance
    # resistance = grid1.Rpt
    # print("Grounding Resistance (Ohms):", resistance)

    # print("self.Rpt", grid1.Rpt)
    # print("self.Lt", grid1.Lt)
    # print("self.Lc", grid1.Lc)
    # print("self.kii", grid1.kii)
    # print("self.kh", grid1.kh)
    # print("self.Dm", grid1.Dm)
    # print("self.n", grid1.n)
    # print("self.na", grid1.na)
    # print("self.nb", grid1.nb)
    # print("self.nc", grid1.nc)
    # print("self.nd", grid1.nd)
    # print("self.km_first", grid1.km_first)
    # print("self.km_second", grid1.km_second)
    # print("self.km_third", grid1.km_third)
    # print("self.km_fourth", grid1.km_fourth)
    # print("self.km_fifth", grid1.km_fifth)
    # print("self.km_sixth", grid1.km_sixth)
    # print("self.km_seventh", grid1.km_seventh)
    # print("self.km", grid1.km)
    # print("self.ki", grid1.ki)
    # print("self.Lm", grid1.Lm)
    # print("self.ks", grid1.ks)

    # # Calculate touch potential
    # grid1.calc_Em(Ig)
    # touch_potential = grid1.Em
    # print("Touch Potential (Volts):", touch_potential)

    # # Calculate step potential
    # step_potential = grid1.Es(Ig)
    # print("Step Potential (Volts):", step_potential)