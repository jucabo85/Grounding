import sys
import os
from pathlib import Path
import pytest
import numpy as np


# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ..parser.parser import process_dxf
from ..calcs.calc_cable_size import cable_sizing
from ..calcs.calc_tolerables import Etouch,Estep,surface_correction
from ..calcs.calc_rpt import Rpt


@pytest.fixture
def sample_values():

    #Using values from IEEE 80 appendix B

    ro=400                      # Ohm-m
    ros=2500                    # Ohm-m
    depth_crushed_rock=0.102    # 4 inches
    fault_duration=0.5          # seconds
    person_weight=70            # kg
    short_circuit=20            # kA
    split_factor=1              # unitless
    
    return ro,ros,depth_crushed_rock,fault_duration,person_weight,short_circuit,split_factor

@pytest.fixture
def sample_values_rpt():
    ro=400
    side1=70
    side2=35
    side3=side1
    side4=side2
    nrods=24
    rod_length=7.5
    D=7
    A=1
    Lt=1
    rod_diam=5/8*25.4/1000
    depth=0.5
    diam_cond=1/100

    return ro,side1,side2,side3,side4,nrods,rod_length,D,A,Lt,rod_diam,depth,diam_cond

def test_surface_correction(sample_values):
    ro,ros,depth_crushed_rock,fault_duration,person_weight,short_circuit,split_factor=sample_values
    surface_correction_factor=surface_correction(ro,ros,depth_crushed_rock)
    np.testing.assert_almost_equal(surface_correction_factor, 0.74, decimal=0.1) #Note that the value is bigger than the one in the example because they round Cs to 0.74, while I am calculating to 3 decimal places

def test_Etouch(sample_values):
    ro,ros,depth_crushed_rock,fault_duration,person_weight,short_circuit,split_factor=sample_values
    surface_correction_factor=surface_correction(ro,ros,depth_crushed_rock)
    tolerables_values_touch=Etouch(ros,surface_correction_factor,fault_duration,weight=person_weight)
    np.testing.assert_almost_equal(tolerables_values_touch, 838.2, decimal=-1) #Note that the value is bigger than the one in the example because they round Cs to 0.74, while I am calculating to 3 decimal places
    # assert tolerables_values_touch == 838.2
    
def test_Estep(sample_values):
    ro,ros,depth_crushed_rock,fault_duration,person_weight,short_circuit,split_factor=sample_values
    surface_correction_factor=surface_correction(ro,ros,depth_crushed_rock)
    tolerables_values_step=Estep(ros,surface_correction_factor,fault_duration,weight=person_weight)
    np.testing.assert_almost_equal(tolerables_values_step, 2686.6, decimal=-1) #Note that the value is bigger than the one in the example because they round Cs to 0.74, while I am calculating to 3 decimal places
    # assert tolerables_values_step == 2686.6

def test_Rpt(sample_values_rpt): # for example 4 IEEE 80 Appendix B
    ro,side1, side2, side3, side4, nrods, rod_length, D,A, Lt, rod_diam,depth,diameter_cond = sample_values_rpt
    rpt = Rpt(ro, A, Lt, depth, diameter_cond, nrods, rod_length, rod_diam, side1, side2, side3, side4, D, shape="L", case="Sverak")
    expected_rpt = 2.74  # Expected value from IEEE 80 Appendix B example 4
    np.testing.assert_almost_equal(rpt, expected_rpt, decimal=2)
