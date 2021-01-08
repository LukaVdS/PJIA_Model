# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 11:22:30 2020

@author: Luka
"""
#import numpy as np
import math
    
# =============================================================================
#  Calculate the next position       
# =============================================================================
def calculation_next_pos(agent, destination):
    # calculate difference in distance on both axes
    dx = destination[0] - agent.pos[0]
    dy = destination[1] - agent.pos[1]
    
    # calculate distance to parking spot
    distance_to_destination = math.sqrt(dx**2 + dy**2)
    
    # If distance to destination is larger than the speed in one step:
    if distance_to_destination > agent.speed:
        # calculate the angle/heading:
        heading = math.atan2(dy, dx)
        new_pos = [math.cos(heading)*agent.speed + agent.pos[0], math.sin(heading)*agent.speed + agent.pos[1]]
    
    # If the distance is smaller, than the next position is the destination
    elif distance_to_destination <= agent.speed:
        new_pos = destination
    
    # Return the new position
    return new_pos

