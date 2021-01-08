# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 10:59:20 2020

@author: Luka
"""

import numpy as np
from mesa import Agent

from .PJIA_aircraft import Aircraft#, Cargo
#from PJIA_CoordinatingAgent import CoordinatingAgent
from ..General_functions import calculation_next_pos
from ..model_objects.PJIA_Equipment import Equipment

class OffloadingAgent(Agent):
    
    # =========================================================================
    # Create a new Offloader agent
    #
    # Args:
    #     unique_id: Unique agent identifier.
    #     pos: position
    #     waiting_pos: default waiting position
    #     speed: Distance to move per step.
    #
    # =========================================================================

    def __init__(
            self,
            unique_id,
            model,
            pos,
            waiting_pos,
            speed
    ):
        
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.waiting_pos = np.array(waiting_pos) # default position
        self.speed = speed
        self.own_speed = speed

        ## Create empty lists and variables
        # Regarding task and destination
        self.ac_to_offload = [] # Aircraft that have been checked and communicated by the coordinator
        self.destination_position = [] # Destination = first item on the self.ac_to_offload list
        self.destination_agent = []
        # Regarding objects
        self.cargo = []
        self.driving_equipment = 0
        # Regarding interactions and actions
        self.interacting_agent = 0
        self.interaction_state = 0
        self.last_waiting_counter = 0
        self.previous_state = 0
        self.waiting_counter = 0
        
        
        self.offloader_state = 'waiting'
        # offloader_state : 
        #   waiting (= waiting to get a job)  
        #   moving (= going to or back from destination)
        #   interacting (= with aircraft or coordinator, standing in place)
        #   offloading (= bringing cargo back from aircraft)
        
        
    # =============================================================================
    #  Determine the next destination of the aircraft agent       
    # =============================================================================
    def determine_next_destination(self):
        # Need to know the agent ID and the position, default is going to waiting_pos
        destination_position = self.waiting_pos
        destination_agent = 0
        
        # If there are aircraft to offload
        if len(self.ac_to_offload) > 0:
            
            # If the offloader is not driving, go to equipment
            if self.offloader_state == 'walking':
                for equipment in self.model.schedule.agents:
                    if type(equipment) is Equipment:
                        destination_position = equipment.pos
                        destination_agent = equipment
                        equipment.equipment_state = 'used'
                        
            # If the offloader is driving, go to destination (aircraft) agent with driving speed            
            elif self.offloader_state == 'driving':
                for agent in self.model.schedule.agents:
                    
                    if type(agent) is Aircraft:
                        # If the agent is equal to the first agent on the offload list:
                        if self.ac_to_offload[0] == agent:
                            # Set that agent as the destination
                            destination_position = agent.pos
                            destination_agent = agent

        return destination_position, destination_agent

    # =============================================================================
    #  Determine the interactions of the offloading agent
    #  The agent in the lead determines the action/states during interaction 
    #       Offloader is leading in: aircraft
    #       Offloader is not in the lead in : coordinator
    # =============================================================================
    def interacting(self, interacting_agent):
        self.waiting_counter += 1
        
        #  From the aircraft need the cargo to offload, the aircraft can exit 
        #  if offloading has been finished
        if type(interacting_agent) is Aircraft:
            # New position is position of aircraft
            new_position = interacting_agent.pos
            # Change aircraft state to offloading
            interacting_agent.aircraft_state = 'Offloading'
            
# =============================================================================
#    Should only be used if offloader is in the lead with multiple agent types
# =============================================================================
#             # In case the waiting counter has been interupted by another interaction
#             if not self.waiting_counter == (self.last_waiting_counter + 1):
#                 # Set the waiting counter to previous 
#                 self.waiting_counter = self.last_waiting_counter
#             # Safe the new waiting counter as the previous one
#             self.last_waiting_counter = self.waiting_counter
# =============================================================================
            
            # When the interaction time has been exceeded
            if self.waiting_counter >= self.model.interaction_aircraft_offloader:
                # Reset waiting counters                
                self.waiting_counter = 0
                self.last_waiting_counter = 0
                # Interaction is over and the offloader starts offloading/brining cargo back
                self.offloader_state = 'offloading'
                self.interacting_agent = 0
                self.ac_to_offload.remove(interacting_agent)
                # Aircraft can start exiting
                interacting_agent.aircraft_state = 'Exitting'
                self.cargo = interacting_agent.cargo
                interacting_agent.cargo = []
                
        # Only if the coordinator is in the lead, so no action needed for offloader
        else:
            new_position = self.pos
            
        return new_position
                

#######################################################################################################
#######################################################################################################
    # =============================================================================
    #  Moving to from waiting position to aircraft and back,
    #  order of aircraft according to waiting time.    
    # =============================================================================
        # offloader_state : 
        #   waiting (= waiting to get a job)  
        #   moving (= going to or back from destination)
        #   interacting (= with aircraft or coordinator, standing in place)
        #   offloading (=  bringing cargo back from aircraft)
        
    def move(self):
        # Waiting to get a job/target/destination
        if self.offloader_state == 'waiting':
            new_position = self.pos
            # If there are aircraft in the list to offload, start moving
            if len(self.ac_to_offload) > 0: # !!! check if equipment is free !!!
                self.offloader_state = 'walking'
        
        # Going to or back from a destination, bringing cargo back is not included
        elif self.offloader_state == 'walking':
            # determine the destination
            self.destination_position, self.destination_agent = self.determine_next_destination()
            new_position = calculation_next_pos(self, self.destination_position)
            
            # If the agent arrived at is waiting position
            if np.array_equal(new_position, self.waiting_pos):
                self.offloader_state = 'waiting'
            
            # If the agent arrived at its destination, which is the equipment
            elif np.array_equal(new_position, self.destination_position):
                self.offloader_state = 'driving'
                self.driving_equipment = self.destination_agent
                self.speed = self.driving_equipment.speed
        
        # If the offloader is driving the equipment (towards the aircraft)
        elif self.offloader_state == 'driving':
            self.destination_position, self.destination_agent = self.determine_next_destination()
            new_position = calculation_next_pos(self, self.destination_position)
            self.driving_equipment.pos = new_position
            # If the agent arrives at its destination, which is an aircraft
            if np.array_equal(new_position, self.destination_position):
                self.offloader_state = 'interacting'
        
        # Interacting with another agent
        elif self.offloader_state == 'interacting':
            # When the interaction with an aircraft is interupted by a coordinator
            # !!! Add interacting with cargo !!!
            if not self.interaction_state == 'interupted':
                self.interacting_agent = self.destination_agent
                
            # Stay in position while interacting with another agent
            new_position = self.interacting(self.interacting_agent)
        
        # When the offloader is bringing the cargo back, driving the equipment
        elif self.offloader_state == 'offloading':
            print(self.model.terminal_building_pos)
            new_position = calculation_next_pos(self, self.model.terminal_building_pos)
            
            # Move the cargo as well
            for cargo in self.cargo:
                cargo.pos = new_position
            # Also move the equipment
            self.driving_equipment.pos = new_position
            
            # When cargo is offloaded and offloader is at its building 
            if np.array_equal(new_position, self.model.terminal_building_pos):
                # If more aircraft to offload, go driving towards new aircraft
                if len(self.ac_to_offload) > 0:
                    self.offloader_state = 'driving'
                # Else, offloader is finished
                else:
                    self.offloader_state = 'finished'
                    
        # When the offloader has no new aircraft to offload            
        elif self.offloader_state == 'finished':
            # Go to equipment parking spot
            new_position = calculation_next_pos(self, self.driving_equipment.parking_pos)
            self.driving_equipment.pos = new_position
            
            # If arrived at equipment driving spot
            if np.array_equal(new_position, self.driving_equipment.parking_pos):
                # Change state of equipment and offloader
                self.driving_equipment.equipment_state = 'parked'
                self.offloader_state = 'walking'
                # Reset the variables
                self.driving_equipment = 0
                self.speed = self.own_speed
                  
        # Move to new position 
        self.model.space.move_agent(self, new_position)
        
    # =============================================================================
    #  Step function       
    # =============================================================================
    def step(self):          
        if self.offloader_state == 'waiting' or  self.offloader_state == 'walking' or self.offloader_state == 'driving' or self.offloader_state == 'interacting' or self.offloader_state == 'offloading' or  self.offloader_state == 'finished':
            self.move() 
     
        else:
            print(self.offloader_state)
            raise Exception("Offloader state is not possible")

        
#######################################################################################################
#######################################################################################################

