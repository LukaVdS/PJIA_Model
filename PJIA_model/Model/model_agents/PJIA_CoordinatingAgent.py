# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 11:16:06 2020

@author: Luka
"""

import numpy as np
from mesa import Agent

from .PJIA_aircraft import Aircraft
from .PJIA_OffloadingAgent import OffloadingAgent
from ..General_functions import calculation_next_pos

class CoordinatingAgent(Agent):
    
    # =========================================================================
    # Create a new Coordinator agent
    #
    # Args:
    #     unique_id: Unique agent identifier.
    #     pos: position
    #     waiting_pos: default waiting position
    #     speed: Distance to move per step.
    #     coordinator_memory: Amount of aircraft (information) it can memorise 
    #
    # =========================================================================
    def __init__(
            self,
            unique_id,
            model,
            pos,
            waiting_pos,
            speed,
            coordinator_memory
    ):

        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.waiting_pos = np.array(waiting_pos)
        self.speed = speed
        self.coordinator_memory = coordinator_memory

        # Create empty lists and variables
        self.destination_position = []
        self.destination_agent = []
        self.checked_ac = []
        self.old_checked_ac = []

        self.interacting_agent = 0
        self.waiting_counter = 0
        
        # Starting state
        self.coordinator_state = 'waiting'    
        # coordinator_state : 
        #   waiting (= waiting to get a job)  
        #   moving (= going to or back from destination)
        #       to aircraft, offloader or default/waiting position
        #   interacting (= with aircraft or coordinator, standing in place)
        #       aircraft, offloader
        
    # =============================================================================
    #  Determine the next destination of the coordinating agent       
    # =============================================================================
    def determine_next_destination(self):
        # Find all parked aircraft
        waiting_list = []
        position_list = []
        agent_list = []
        
        # If there are less than aircraft checked than memory allows
        if len(self.checked_ac) < self.coordinator_memory:
            
            # looking for the longest waiting aircraft
            for agent in self.model.schedule.agents:
                if type(agent) is Aircraft:
                    # If the aircraft is parked and the aircraft has not been checked before...
                    if agent.aircraft_state == 'Parked' and (agent not in self.checked_ac) and (agent not in self.old_checked_ac):
    
                        ### Append the aircraft to the list           
                        waiting_list.append(agent.waiting_counter)
                        position_list.append(agent.parking_pos)
                        agent_list.append(agent)
    
            # If there are aircraft waiting to be checked  
            if len(waiting_list) > 0:
                # Getting index of the longest waiting aircraft
                indexer = waiting_list.index(max(waiting_list))
                # Use index to get the ID and position of that aircraft
                destination_position = position_list[indexer]
                destination_agent = agent_list[indexer]
                
            # If there are no new aircraft to check, but there are aircraft memorised   
            elif len(self.checked_ac)> 0:
                # Go to offloader building
                for agent in self.model.schedule.agents:
                    if type(agent) is OffloadingAgent:
                        destination_position = agent.waiting_pos
                        destination_agent = agent
                        
            # If there are no new aircraft to check, but there are also no aircraft memorised             
            else:
                # Go to own building
                destination_position = self.waiting_pos
                destination_agent = []
        
        # If memory of coordinator is full                
        elif len(self.checked_ac) == self.coordinator_memory:
            # Go to offloader building
            for agent in self.model.schedule.agents:
                    if type(agent) is OffloadingAgent:
                        destination_position = agent.waiting_pos
                        destination_agent = agent
            
        return destination_position, destination_agent
    
    # =============================================================================
    #  Determine the interactions of the coordinating agent
    #  The agent in the lead determines the action/states during interaction 
    #       Coordinator is leading in: aircraft, offloader
    #       Coordinator is not in the lead in : /      
    # =============================================================================
    def interacting(self, interacting_agent):
        self.waiting_counter += 1
        
        # From the aircraft, need information (amount cargo, type cargo)
        if type(interacting_agent) is Aircraft:
            # New position is position of aircraft
            new_position = interacting_agent.pos
            
            # When the interaction time has been exceeded
            if self.waiting_counter >= self.model.interaction_aircraft_coordinator: 
                # Coordinator starts moving again
                self.coordinator_state = 'moving'
                # The waiting counter gets reset
                self.waiting_counter = 0
                # The aircraft goes to the checked aircraft list
                self.checked_ac.append(self.interacting_agent)
                # Reset the interacting agent
                self.interacting_agent = 0
        
        # From the offloader, give aircraft information (amount cargo, type cargo, order to offload)
        elif type(interacting_agent) is OffloadingAgent: 
            # New position is the building of the offloader
            new_position = interacting_agent.waiting_pos
            
            # In the first step, save the current state of the offloader
            if self.waiting_counter == 1:
                interacting_agent.previous_state = interacting_agent.offloader_state
             
            # If the offloader is also in the building
            if np.array_equal(interacting_agent.waiting_pos, interacting_agent.pos):
                # Change state of offloader to interacting and interupted
                interacting_agent.offloader_state = 'interacting'
                interacting_agent.interaction_state = 'interupted'
                interacting_agent.interacting_agent = self
            
            # When the interaction time has been exceeded
            if self.waiting_counter >= self.model.interaction_coordinator_offloader:
                # Reset waiting counter
                self.waiting_counter = 0
                # Extend the offloader agents list of aircraft to be offloaded
                interacting_agent.ac_to_offload.extend(self.checked_ac) # !!! can only know when offloader is back?
                # Put the list of checked aircraft in the 'archive'
                self.old_checked_ac = self.destination_agent.ac_to_offload
                # Make memory free, so new aircraft can be checked
                self.checked_ac = []
                
                # If the state of the offloader was interupted
                if np.array_equal(interacting_agent.waiting_pos, interacting_agent.pos):
                    # Raise warning when offloader has no 'previous state'
                    if interacting_agent.previous_state == 0:
                        raise Exception('Offloader has no previous state to go back to!')
                    # Reset all interacting agent's parameters
                    interacting_agent.interaction_state = 0
                    interacting_agent.offloader_state = interacting_agent.previous_state
                    interacting_agent.interacting_agent = 0
                    interacting_agent.previous_state = 0
                
                # Reset coordinator agent parameters
                self.coordinator_state = 'moving'
                self.interacting_agent = 0
                
        # If other agent is in the lead, stay in place
        ## !!! At the moment not the case !!!
        else:
            new_position = self.pos
            self.waiting_counter = 0
                
        return new_position
    
    # =============================================================================
    #  Moving to from waiting position to aircraft and back,
    #  order of aircraft according to waiting time.    
    # =============================================================================
        # coordinator_state : 
        #   waiting (= waiting to get a job)  
        #   moving (= going to or back from destination)
        #   interacting (= with aircraft or coordinator, standing in place)
        
    def move(self):
        
        # When no aircraft, stay at waiting position (building)
        if self.coordinator_state == 'waiting':
            new_position = self.waiting_pos
            
            # Look for destinations
            self.destination_position, self.destination_agent = self.determine_next_destination()
            # If the destination is not the waiting position
            if not np.array_equal(self.waiting_pos, self.destination_position):
                # Start moving!
                self.coordinator_state = 'moving'
        
        # The coordinator is moving
        elif self.coordinator_state == 'moving':
            # Keep checking the destination
            self.destination_position, self.destination_agent = self.determine_next_destination()
            new_position = calculation_next_pos(self, self.destination_position)
            
            # If the destination is the waiting position, wait for new destination
            if np.array_equal(new_position, self.waiting_pos):
                self.coordinator_state = 'waiting'
            # If the coordinator has arrived at its destination, start interacting
            if np.array_equal(new_position, self.destination_position):
                self.coordinator_state = 'interacting'
                self.interacting_agent = self.destination_agent
                    
        # Coordinator interacting position is position of the interacting agent             
        elif self.coordinator_state == 'interacting':            
            new_position = self.interacting(self.interacting_agent)
               
        # Move to new position 
        self.model.space.move_agent(self, new_position)
        
    # =============================================================================
    #  Step function       
    # =============================================================================
    def step(self):          
        if self.coordinator_state == 'waiting' or self.coordinator_state == 'moving' or self.coordinator_state == 'interacting':
            self.move() 
     
        else:
            raise Exception("Coordinator state is not possible")
            