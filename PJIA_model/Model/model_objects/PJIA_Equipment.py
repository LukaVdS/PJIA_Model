# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 11:58:00 2020

@author: Luka
"""

import numpy as np
from mesa import Agent
import math
from Model.General_functions import calculation_next_pos


class Equipment(Agent):
    
    # =========================================================================
    # Create a new Equipment agent
    #
    # Args:
    #     unique_id: Unique agent identifier.
    #     pos: Starting position
    #     parking_pos: parking spot position
    #     speed: Distance to move per step.
    #
    # =========================================================================

    def __init__(
            self,
            unique_id,
            model,
            pos,
            parking_pos,
            speed
    ):
        
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.parking_pos = np.array(parking_pos)
        self.speed = speed
        
        self.equipment_state = 'parked'
        
        # Equipment states:
        #   parked
        #   used
    
        
        

    # =============================================================================
    #  Moving function is solely dependent on the driver
    # =============================================================================

    def move(self):
        new_position = self.pos

        # Move to new position 
        self.model.space.move_agent(self, new_position)
                

            
    # =============================================================================
    #  Step function       
    # =============================================================================
    def step(self):
        self.move()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
