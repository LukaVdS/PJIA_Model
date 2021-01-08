# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 15:56:08 2020

@author: Luka
"""

import numpy as np
from mesa import Agent
import math
from ..General_functions import calculation_next_pos
# from ast import literal_eval


class Aircraft(Agent):
    
    # =========================================================================
    # Create a new Aircraft agent
    #
    # Args:
    #     unique_id: Unique agent identifier.
    #     pos: Starting position
    #     parking_pos: parking spot position
    #     exit_pos: position of exit
    #     speed: Distance to move per step.
    #     arrival_time = step of the model at which the flight should depart its origin
    #     n_cargo = amount of cargo the aircraft is carrying
    #     schedule_ID = the ID of the aircraft in the schedule (see parameters.py and aircraft_schedule.xlsx)
    #
    # =========================================================================

    def __init__(
            self,
            unique_id,
            model,
            pos,
            arrival_time,
            speed,
            n_cargo,
            schedule_ID
    ):

        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.parking_pos = 0
        self.speed = speed
        self.arrival_time = arrival_time
        self.n_cargo = n_cargo
        self.schedule_ID = schedule_ID
        
        # Create empty lists and variables
        self.waiting_counter = 0
        self.cargo = [] # self.determine_carried_cargo()
        
        # Define all for parking
        self.amount_parking_spots = 10 # amount of parking spots
        self.nodes = np.array([pos])    # Array of crosspoints/nodes, start with own position
        self.parking_spot_index = 10000 # Index of the parking spot in in self.model.parking_spots (see parking_schedule.xlsx (Sheet1))
        
        
        self.aircraft_state = 'NotArrived'
        # NotArrived :  aircraft has not yet arrived (see aircraft_schedule.xlsx)
        # Taxiing :     going towards parking spot
        # Parked :      parked, gets checked by coordinator
        # Offloading :  offloader is offloading
        # Exitting :    offloader is finished, aircraft can leave
        # Gone :        aircraft has left

                
        # =============================================================================
        #  Taxi route        
        # =============================================================================
        
    # =============================================================================
    #  Determine which taxi route the aircraft needs to take to exit
    # =============================================================================
    def determine_taxi_route_to_exit(self):
        nodes = np.array([self.parking_pos])
        
        if self.parking_spot_index < 3:
           nodes = np.append(nodes, self.model.route_CP13_E1, axis=0)
           
        elif self.parking_spot_index == 3:
           nodes = np.append(nodes, self.model.route_CP4_E2, axis=0)
        elif self.parking_spot_index == 4:
           nodes = np.append(nodes, self.model.route_CP5_E2, axis=0)
        elif self.parking_spot_index < 7:
           nodes = np.append(nodes, self.model.route_CP67_E2, axis=0)
        elif self.parking_spot_index < 10:
           nodes = np.append(nodes, self.model.route_CP89_E2, axis=0)
       
        self.exit_pos = nodes[len(nodes) -1] 
        
        return nodes
                
    
    # =============================================================================
    #  Determine which taxi route the aircraft needs to take
    # =============================================================================
    def determine_taxi_route_to_parking(self):
        
        ac_Schedule = self.model.aircraft_schedule
        x = ac_Schedule.index[ac_Schedule.Aircraft_ID == self.schedule_ID][0]
        nodes = self.nodes
        
        # Choose parking spot, dependent on starting point
        
        if ac_Schedule.Start_Name[x] == 'S1':
            # all parking spots in preferred order (A, B ,C) 
            all_parking_spots = range(self.amount_parking_spots)
            
        elif ac_Schedule.Start_Name[x] == 'S2':
            # all parking spots in preferred order (5-9, 4-1) 
            all_parking_spots = [4, 5, 6, 7, 8, 3, 2, 1, 0]
            
        # Going over all parking spots in preferre d order           
        for Index_number in all_parking_spots:
            # to check the first one that is free
            print(self.model.CP_spots_occupation)
            if self.model.CP_spots_occupation[Index_number] == 'Free':
                
                # Set parking spot to occupied
                self.model.CP_spots_occupation[Index_number] = 'Occupied'
                # Save the position of the parking spot
                self.parking_pos = self.model.CP_coordinates[Index_number]
                #self.parking_pos = np.array((self.model.parking_spots.Parking_X[Index_number] * self.model.space.x_max, self.model.parking_spots.Parking_Y[Index_number] * self.model.space.y_max)      )
                
                # Save the 'name' of the parking spot (A, B or C)
                self.parking_ID = self.model.CP_spots_name[Index_number]
                # Save the Index number 
                self.parking_spot_index = Index_number
                break
        
        if ac_Schedule.Start_Name[x] == 'S1':
            if self.parking_spot_index < 4:
                nodes = np.append(nodes, self.model.route_S1_CP14, axis=0)
                
            elif self.parking_spot_index == 4:
                nodes = np.append(nodes, self.model.route_S1_CP5, axis=0)
                
            elif self.parking_spot_index == 5:
                nodes = np.append(nodes, self.model.route_S1_CP6, axis=0)
                
            elif self.parking_spot_index == 6:
                nodes = np.append(nodes, self.model.route_S1_CP7, axis=0)
            
            else:
                nodes = np.append(nodes, self.model.route_S1_CP89, axis=0)
            
            
        elif ac_Schedule.Start_Name[x] == 'S2':
            if self.parking_spot_index < 4:
                nodes = np.append(nodes, self.model.route_S2_CP14, axis=0)
                
            elif self.parking_spot_index == 5:
                nodes = np.append(nodes, self.model.route_S2_CP5, axis=0)
                
            elif self.parking_spot_index == 6:
                nodes = np.append(nodes, self.model.route_S2_CP6, axis=0)
                
            elif self.parking_spot_index ==7:
                nodes = np.append(nodes, self.model.route_S2_CP7, axis=0)
            
            else:
                nodes = np.append(nodes, self.model.route_S2_CP89, axis=0)
                
        nodes = np.append(nodes,[self.parking_pos], axis=0)
                    
        return nodes 

    # =============================================================================
    #   Calculation of the next position of the aircraft, 
    #   depending on the nodes and the speed
    # =============================================================================
    def calculation_next_taxi_step(self, nodes):
        # Create starting variables
        distance_to_destination = 0 # destination is the next node in the list
        distance_travelled = 0
        steps_left = self.speed
        pos = self.pos
        counter = 0
        print(nodes)
        # As long as the distance to destination is smaller than the amount 
        # of steps left.
        while distance_to_destination < steps_left:
            # calculate difference in distance on both axes
            destination = nodes[0]
            dx = destination[0] - pos[0]
            dy = destination[1] - pos[1]
            # calculate distance to parking spot
            distance_to_destination = math.sqrt(dx**2 + dy**2)
            
            # calculate how many steps can be taken
            steps_left = self.speed - distance_travelled
            
            # If the new position will not pass the destination: 
                # So all steps_left can be taken before the destination (next node)
            if distance_to_destination > steps_left:
                # calculate the angle/heading:
                heading = math.atan2(dy, dx)
                # calculate the next position
                new_pos = [round(math.cos(heading)*steps_left + pos[0]), round(math.sin(heading)*steps_left + pos[1])]
                break
            
            # Else if the destination is the last node in the list:
            elif len(nodes) == 1:
                new_pos = destination
                break
            
            # Else if the new position is the destination
            elif steps_left == distance_to_destination:
                new_pos = destination
                nodes = np.delete(nodes, 0, axis=0)
                if self.aircraft_state == 'Taxiing':
                    self.nodes = nodes
                elif self.aircraft_state == 'Exitting':
                    self.nodes_exit = nodes
                break
            
            # Else if the new position is not reached yet
            elif distance_to_destination < steps_left:
                # The distance travelled to the node
                distance_travelled += distance_to_destination
                # Set the old destination as the new starting point
                pos = nodes[0]
                # Delete the old destination from the destination list
                nodes = np.delete(nodes, 0, axis=0)
                
                if self.aircraft_state == 'Taxiing':
                    self.nodes = nodes
                elif self.aircraft_state == 'Exitting':
                    self.nodes_exit = nodes
                    
                # Add a safety counter, to not get stuck in an infinite loop
                counter += 1
                print('another loop', steps_left, 'steps left')
                
                if counter > 10:
                    new_pos = pos
                    print('aircraft passed 10 nodes and is not at its next destination!')
                    break
                
        return new_pos
    

    # =============================================================================
    #  Determine which cargo the aircraft is carrying which itself
    # =============================================================================
    def determine_carried_cargo(self):
        cargo_list = []
        
        # If a cargo object has the same schedule ID as the aircraft, 
            # means that the cargo is carried by the aircraft
        for agent in self.model.schedule.agents:
            if type(agent) is Cargo:
                if agent.schedule_ID == self.schedule_ID:
                    cargo_list.append(agent)
                    
        return cargo_list



    # =============================================================================
    #  Moving function has 5 stages. Starting when landed, then taxii to parking spot
    #  Waiting at the parking spot untill it gets offloaded, when offloader is gone,
    #  go to exit point and dissappear.
    # =============================================================================
    
        # NotArrived :  aircraft has not yet arrived (see aircraft_schedule.xlsx)
        # Taxiing :     going towards parking spot
        # Parked :      parked, gets checked by coordinator
        # Offloading :  offloader is offloading
        # Exitting :    offloader is finished, aircraft can leave
        # Gone :        aircraft has left

    def move(self):
        # If the aircraft has not yet arrived at its exit point
        if not self.aircraft_state == 'Gone': 
            
            # Aircraft can only move after it has arrived                
            if self.model.schedule.steps >= self.arrival_time:
                # Aircraft has just started flying
                if self.aircraft_state == 'NotArrived':
                    self.aircraft_state = 'Taxiing'
                    # Determine which cargo is carries by aircraft
                    self.cargo = self.determine_carried_cargo()
                    # Determine all the nodes for the correct taxi route to parking
                    self.nodes = self.determine_taxi_route_to_parking()
                    self.nodes_exit = self.determine_taxi_route_to_exit()
                
                # If going towards parking
                if self.aircraft_state == 'Taxiing':
                    # Calculate next position by using the defined nodes:
                    new_position = self.calculation_next_taxi_step(self.nodes)
                    # Change the position of the cargo in aircraft
                    for cargo in self.cargo:
                        cargo.pos = new_position
                    # If the aircraft has arrived at the parking space
                    if np.array_equal(new_position, self.parking_pos):
                        self.aircraft_state = 'Parked'
                        
                # If on parkinglot, wait for the offloader
                elif self.aircraft_state == 'Parked':
                    new_position = self.pos
                    for cargo in self.cargo:
                        cargo.pos = new_position
                    self.waiting_counter += 1
                
                # If offloader has arrived
                elif self.aircraft_state == 'Offloading':
                    new_position = self.pos
                    # Waiting counter is for the offloader
                    self.waiting_counter = 0
                    
                # If going towards exit
                elif self.aircraft_state == 'Exitting':
                    new_position = self.calculation_next_taxi_step(self.nodes_exit)
                    self.model.CP_spots_occupation[self.parking_spot_index] = 'Free'
# =============================================================================
#                     # If the parking_spot_index is a valid index in the parking spot list
#                     if self.parking_spot_index <= len(self.model.parking_spots):
#                         #  Set the parking spot state to 'free' again
#                         self.model.parking_spots.Occupation[self.parking_spot_index] == 'Free'
#                         # Set the parking_spot_index to a unrealisticly high number
#                         self.parking_spot_index = len(self.model.parking_spots) + 100
#                         
#                     new_position = calculation_next_pos(self, self.exit_pos)
# =============================================================================
                    
                    # When arrived at exit point, change status to 'Gone'
                    if np.array_equal(new_position,self.exit_pos):
                        # If the agent is within reach of its destination, the state is changed to 'Gone'
                        self.aircraft_state = 'Gone'
                        self.model.exited_aircraft += 1
                        
                
                # Move to new position 
                self.model.space.move_agent(self, new_position)
                

            
    # =============================================================================
    #  Step function       
    # =============================================================================
    def step(self):
        # Aircraft can only move after it has arrived and before it exited
        #if not self.aircraft_state == 'NotArrived' or self.aircraft_state == 'Gone':
        self.move() 



'''############################################################################
###############################################################################
###############################################################################
'''
class Cargo(Agent):
    
    # =========================================================================
    # Create a new Equipment agent
    #
    # Args:
    #     unique_id: Unique agent identifier.
    #     pos: Starting position
    #
    # =========================================================================

    def __init__(
            self,
            unique_id,
            model,
            pos,
            schedule_ID
    ):
        
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        
        self.schedule_ID = schedule_ID
        
        self.cargo_state = 'aircraft'
        
        self.speed = 0
                
        
        # Cargo states (not applied yet):
        #   static
        #   carried/interacting
        #       interacting states:
        #       - aircraft
        #       - offloader
        #       - vehicle
        
    # =============================================================================
    #  Moving function is solely dependent on other agents
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
     
        