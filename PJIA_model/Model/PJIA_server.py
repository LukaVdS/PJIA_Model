# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 15:55:56 2020

@author: Luka
"""
from mesa.visualization.ModularVisualization import ModularServer
from .PJIA_model import PJIAModel
from .SimpleContinuousModule import SimpleCanvas
from .model_agents.PJIA_aircraft import Aircraft, Cargo
from .model_agents.PJIA_OffloadingAgent import OffloadingAgent
from .model_agents.PJIA_CoordinatingAgent import CoordinatingAgent
from .model_objects.PJIA_Equipment import Equipment
from parameters import model_params, canvas_ratio, width_canvas

import sys, asyncio
import random
if sys.version_info[0]==3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# =============================================================================
# Define the drawing of agents
# =============================================================================
def draw_aircraft(agent):
    if type(agent) is Aircraft:
        return {"Shape": "circle", "Filled": "true", "Layer": 0, "Color": "black", "r": 5.5}
    
    elif type(agent) is OffloadingAgent:
        return {"Shape": "circle", "Filled": "true", "Layer": 2, "Color": "green", "r": 2}
    
    elif type(agent) is CoordinatingAgent:
        return {"Shape": "circle", "Filled": "true", "Layer": 1, "Color": "red", "r": 2}
    
    elif type(agent) is Equipment:
        return {"Shape": "rect", "Filled": "false", "Layer": 0, "Color": "blue", "w": 0.01, "h": 0.01/canvas_ratio}
        #return {"Shape": "circle", "Filled": "false", "Layer": 0, "Color": "blue", "r": 2.5}
        
    elif type(agent) is Cargo:
        return {"Shape": "rect", "Filled": "false", "Layer": 3, "Color": "yellow", "w": 0.005, "h": 0.005/canvas_ratio}
        #return {"Shape": "circle", "Filled": "false", "Layer": 0, "Color": "blue", "r": 2.5}
    


        
   
# =============================================================================
# Define the canvas and the agents in it
# =============================================================================
height_canvas = width_canvas*canvas_ratio

airport_canvas = SimpleCanvas(draw_aircraft, width_canvas, height_canvas) 

server = ModularServer(PJIAModel, [airport_canvas], "PJIA Model", model_params)

server.port = random.randrange(8500, 9000)

#server.port = 8523
#server.launch()



# chart = ChartModule([{"Label": "Total Fuel Used", "Color": "Black"}],
#                     data_collector_name='datacollector')
# chart = ChartModule([{"Label": "Amount of formations", "Color": "Black"}],
#                     data_collector_name='datacollector')
# chart1 = ChartModule([{"Label": "Agents in a formation", "Color": "Blue"}],
#                     data_collector_name='datacollector')
# server = ModularServer(FormationFlying, [formation_canvas, chart, chart1], "Formations", model_params)


#server.launch()