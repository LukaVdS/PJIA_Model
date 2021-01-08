# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 11:04:21 2020

@author: Luka
"""
import pandas as pd

canvas_ratio = 480./1100
width_canvas = 1000

# Model parameters, can be set here:
model_params = {
    # Define canvas
    "width" :width_canvas, 
    "height" : width_canvas*canvas_ratio,
    # Define agents
    "n_offloaders" : 1,
    "offloaders_speed" : 5,
    "coordinator_memory" : 2,
    "equipment_speed" : 10,
    # Define actions of agents
    "arrival_window" : 30,
    "interaction_aircraft_offloader" : 10,
    "interaction_coordinator_offloader" : 5,
    "interaction_aircraft_coordinator" : 5,
    # Define positions [% of canvas]
    "offloaders_position" : [0.05, 0.35],
    "coordinator_position" : [0.6, 0.45],
    "equipment_position" : [0.05, 0.5],
    "terminal_building_pos" : [0.27, 0.20]
    } 
    

# =============================================================================
### Imported tables from Excel
# =============================================================================
# Schedule of aircraft, with schedule_ID, amount of cargo, cargo type and starting point
acSchema = pd.read_excel(r'.\Model\TablesAndFigures\aircraft_schedule.xlsx') 
# Table with all coordinates of the visualisation part of the model (starting points, exit points, taxi nodes, parking spot coordinates)
airport_coordinates = pd.read_excel(r'.\Model\TablesAndFigures\parking_schedule.xlsx',sheet_name='Sheet2') 
# =============================================================================

# Multiple iterations are used when running the batchrunner.py:
n_iterations = 2