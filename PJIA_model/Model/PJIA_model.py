# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 12:11:15 2020

@author: Luka
"""
import numpy as np
import math 
np.seterr(all='raise')

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation # This line has changed in V9 on 13-oct.
from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner
import pandas as pd
from parameters import acSchema, airport_coordinates

import time

from .model_agents.PJIA_aircraft import Aircraft, Cargo
from .model_agents.PJIA_OffloadingAgent import OffloadingAgent
from .model_agents.PJIA_CoordinatingAgent import CoordinatingAgent
from .model_objects.PJIA_Equipment import Equipment
# =============================================================================
#  Move to PJIA_model !!!
# =============================================================================

# def read_aircraft_schedule(model):
#     aircraft_schedule = pd.read_excel(r'C:\Users\Luka\OneDrive\Documents\Afstuderen_niet_dropbox\PJIA_model\aircraft_schedule.xlsx') 
#     ## If you want to have specific column:
#     aircraft_in_schedule = pd.DataFrame(aircraft_schedule, columns= ['Aircraft_ID', 'Arrival', 'Speed'])
#     return aircraft_in_schedule


class PJIAModel(Model):
    """A model with some number of agents."""
    def __init__(self,
                 # Define canvas
                width=1000, 
                height=1000*480./1100,
                # Define agents
                n_offloaders = 1,
                offloaders_speed = 5,
                coordinator_memory = 2,
                equipment_speed = 10,
                # Define actions of agents
                arrival_window = 30,
                interaction_aircraft_offloader = 10,
                interaction_coordinator_offloader = 5,
                interaction_aircraft_coordinator = 5,
                # Define positions [% of canvas]
                offloaders_position = [0.1, 0.2],
                coordinator_position = [0.05, 0.5],
                equipment_position = [0.2, 0.1],
                terminal_building_pos = [0.25, 0.21]
                 ): 
        
        # Define canvas
        self.space = ContinuousSpace(width, height, False)
        self.airport_coordinates = airport_coordinates
        
        # Define aircraft agents 
        self.aircraft_schedule = acSchema
        self.n_aircraft = len(self.aircraft_schedule.Arrival)
        self.total_amount_cargo = sum(self.aircraft_schedule.Cargo)

        # Define coordinator agents
        self.coordinator_position = coordinator_position
        self.coordinator_memory = coordinator_memory
        
        # Define the offloaders agents
        self.n_offloaders = n_offloaders
        self.offloaders_position = offloaders_position
        self.offloaders_speed = offloaders_speed
        
        # Define Equipment objects:
        self.equipment_position = equipment_position
        self.equipment_speed = equipment_speed
        
        # Define Cargo objects:
        self.cargo_number = 0 # will be used for later agents/objects
        #self.terminal_building_pos = terminal_building_pos
        self.terminal_building_pos = [terminal_building_pos[0]*self.space.x_max, terminal_building_pos[1]*self.space.y_max]
        
        # Define interactions:
        self.interaction_aircraft_offloader = interaction_aircraft_offloader
        self.interaction_coordinator_offloader = interaction_coordinator_offloader
        self.interaction_aircraft_coordinator = interaction_aircraft_coordinator
        
        
        
# =============================================================================
#         voor taxiing
# =============================================================================
        # Copy the the table from excel
        self.taxi_coordinates_excel = pd.DataFrame.copy(airport_coordinates, deep=True)
        # Multiply the coordinates in excel (which are in percentage) by the width and height of the grid
        self.taxi_coordinates_excel['X_pos'] *= self.space.x_max
        self.taxi_coordinates_excel['Y_pos'] *= self.space.y_max
        
        # make array with only coordinates
        self.taxi_coordinates = np.array([[self.taxi_coordinates_excel['X_pos'][0], self.taxi_coordinates_excel['Y_pos'][0]]])
        
        for i in range(1,len(self.taxi_coordinates_excel)):
            self.taxi_coordinates = np.append(self.taxi_coordinates, [[self.taxi_coordinates_excel['X_pos'][i], self.taxi_coordinates_excel['Y_pos'][i]]], axis=0)
        
        
        # make array with only taxi nodes coordinates:
        self.CP_coordinates = self.taxi_coordinates[13:]
        
        
        # Civilian Parking spots, name and occupation
        #self.CP_spots = {'CP1' : 'Free', 'CP2': 'Free', 'CP3': 'Free', 'CP4': 'Free', 'CP5': 'Free', 'CP6': 'Free', 'CP7': 'Free', 'CP8': 'Free', 'CP9': 'Free', 'CP10': 'Free'}
        #self.CP_spots_occupation = ['Free','Free', 'Free', 'Free', 'Free', 'Free','Free', 'Free','Free']
        self.CP_spots_occupation = ['Free','Free', 'Occupied', 'Free', 'Occupied', 'Free','Free', 'Free','Free']
        self.CP_spots_name = ['CP1', 'CP2', 'CP3', 'CP4', 'CP5', 'CP6', 'CP7', 'CP8', 'CP9']
        
        # Determine all the routes from start point to parking
        self.route_S1_CP14 = np.array([self.taxi_coordinates[0]])
        self.route_S2_CP14 = np.array([self.taxi_coordinates[1], self.taxi_coordinates[0]])
        
        self.route_S1_CP5 = np.array([self.taxi_coordinates[0], self.taxi_coordinates[1]])
        self.route_S2_CP5= np.array([self.taxi_coordinates[1]])
        
        self.route_S1_CP6 = np.array([self.taxi_coordinates[0], self.taxi_coordinates[1], self.taxi_coordinates[2]])
        self.route_S2_CP6 = np.array([self.taxi_coordinates[1], self.taxi_coordinates[2]])
        
        self.route_S1_CP7 = np.array([self.taxi_coordinates[0], self.taxi_coordinates[1], self.taxi_coordinates[2], self.taxi_coordinates[3]]) 
        self.route_S2_CP7 = np.array([self.taxi_coordinates[1], self.taxi_coordinates[2], self.taxi_coordinates[3]])
        
        self.route_S1_CP89 = np.array([self.taxi_coordinates[0], self.taxi_coordinates[1], self.taxi_coordinates[2], self.taxi_coordinates[5]]) 
        self.route_S2_CP89 = np.array([self.taxi_coordinates[1], self.taxi_coordinates[2], self.taxi_coordinates[5]])
      
        # Determine routes from parking to exit
        self.route_CP13_E1 = np.array([self.taxi_coordinates[4], self.taxi_coordinates[7], self.taxi_coordinates[6], self.taxi_coordinates[11]])
        
        self.route_CP4_E2 = np.array([self.taxi_coordinates[1], self.taxi_coordinates[2], self.taxi_coordinates[3], self.taxi_coordinates[12]])
        
        self.route_CP5_E2 = np.array([self.taxi_coordinates[2], self.taxi_coordinates[3], self.taxi_coordinates[12]])
        
        self.route_CP67_E2 = np.array([self.taxi_coordinates[3], self.taxi_coordinates[12]])
        
        self.route_CP89_E2 = np.array([self.taxi_coordinates[5], self.taxi_coordinates[2], self.taxi_coordinates[3], self.taxi_coordinates[12]])
        # =============================================================================

        
        # Define the running
            # Stop when all aircraft have exited
        self.exited_aircraft = 0        
        self.schedule = RandomActivation(self)
            # Make all agents
        self.make_coordinator()
        self.make_offloader()
        self.make_aircraft()
        self.make_equipment()
        self.make_cargo()

        # Start running
        self.running = True
        self.start_time = 0
        self.exit_step = 1000

    # =========================================================================
    #  Create all aircraft, the aircraft are not all initialized at the same time,
    #  but within an arrival window.
    # =========================================================================

    def make_aircraft(self):
        

# =============================================================================
#             # Starting position
#             pos = np.array((aircraft_schedule.Origin_X[i]* self.space.x_max, aircraft_schedule.Origin_Y[i] * self.space.y_max))
#             # Position of parking spot            
#             parking_pos = np.array((aircraft_schedule.Parking_X[i] * self.space.x_max, aircraft_schedule.Parking_Y[i] * self.space.y_max))
# =============================================================================
        
        for i in range(self.n_aircraft):
            # Look for the correct position of the starting point
            for x in range(len(self.airport_coordinates)):
                if self.aircraft_schedule.Start_Name[i] == self.airport_coordinates.Name[x]:
                    Start_X = airport_coordinates.X_pos[x]
                    Start_Y = airport_coordinates.Y_pos[x]
            
            ## Get the aircraft data and schedule from the excel file 'aircraft_schedule'
            # Starting pos
            pos = np.array((Start_X * self.space.x_max, Start_Y * self.space.y_max))
            # # Position of exit
            # exit_pos = np.array((self.aircraft_schedule.Exit_X[i] * self.space.x_max, self.aircraft_schedule.Exit_Y[i] * self.space.y_max))
            # Time the aircraft 'lands'
            arrival_time = self.aircraft_schedule.Arrival[i]
            # Speed of the aircraft
            speed = self.aircraft_schedule.Speed[i]
            # Amount of cargo in the aircraft
            n_cargo = self.aircraft_schedule.Cargo[i]
            # The position/ID in the schedule
            schedule_ID = self.aircraft_schedule.Aircraft_ID[i]
            
            print('I am aircraft', schedule_ID, 'my starting pos is:', pos)
            aircraft = Aircraft(
                i,
                self,
                pos,
                #parking_pos,
                arrival_time,
                speed,
                n_cargo,
                schedule_ID
                )
                
            self.space.place_agent(aircraft, pos)
            self.schedule.add(aircraft)

    # =========================================================================
    #  Create all offloaders
    # =========================================================================

    def make_offloader(self):
        
        for i in range(self.n_offloaders):
            # Starting position is the waiting position
            waiting_pos = np.array((self.offloaders_position[0] * self.space.x_max, self.offloaders_position[1] * self.space.y_max))
            pos = waiting_pos
            speed = self.offloaders_speed
            
            print('I am an offloader and my starting pos is:', pos)
            offloader = OffloadingAgent(
                i + self.n_aircraft,
                self,
                pos,
                waiting_pos,
                speed
                )
                
            self.space.place_agent(offloader, pos)
            self.schedule.add(offloader)
    
    # =========================================================================
    #  Create coordinator
    # =========================================================================

    def make_coordinator(self):
        
        # for i in range(self.n_offloaders):
            # Starting position is the waiting position
            waiting_pos = np.array((self.coordinator_position[0] * self.space.x_max, self.coordinator_position[1] * self.space.y_max))
            pos = waiting_pos
            speed = self.offloaders_speed
            
            print('I am a coordinator and my starting pos is:', pos)
            coordinator = CoordinatingAgent(
                1 + self.n_aircraft + self.n_offloaders,
                self,
                pos,
                waiting_pos,
                speed,
                coordinator_memory = self.coordinator_memory
                )
                
            self.space.place_agent(coordinator, pos)
            self.schedule.add(coordinator)
            
            
    # =========================================================================
    #  Create equipment for offloading
    # =========================================================================
        
    def make_equipment(self):
        
        # for i in range(self.n_offloaders):
            # Starting position is the waiting position
            parking_pos = np.array((self.equipment_position[0] * self.space.x_max, self.equipment_position[1] * self.space.y_max))
            pos = parking_pos
            speed = self.equipment_speed

            equipment = Equipment(
                1 + self.n_aircraft + self.n_offloaders + 1,
                self,
                pos,
                parking_pos,
                speed
                )
                
            self.space.place_agent(equipment, pos)
            self.schedule.add(equipment)
     
            
    # =========================================================================
    #  Create cargo
    # =========================================================================
        
    def make_cargo(self):
        cargo_number = 0
        #terminal_building_pos = self.terminal_building_pos
        
        for i in range(self.n_aircraft):
            n_cargo = self.aircraft_schedule.Cargo[i]
            
            # Look for the correct position of the starting point
            for x in range(len(self.airport_coordinates)):
                if self.aircraft_schedule.Start_Name[i] == self.airport_coordinates.Name[x]:
                    Start_X = airport_coordinates.X_pos[x]
                    Start_Y = airport_coordinates.Y_pos[x]
                    break
                
            for j in range(n_cargo):
                ## Starting pos
                pos = np.array((Start_X * self.space.x_max, Start_Y * self.space.y_max))
                # The position/ID in the schedule
                schedule_ID = self.aircraft_schedule.Aircraft_ID[i]
                # Cargo_number for the ID when creating a cargo agent
                cargo_number += 1
                #previous_cargo_number = cargo_number
                cargo = Cargo(
                    cargo_number + self.n_aircraft + self.n_offloaders + 1 + 1, # 1xCoordinator and 1x Equipment
                    self,
                    pos,
                    schedule_ID
                    )
            
                self.space.place_agent(cargo, pos)
                self.schedule.add(cargo)
        self.cargo_number = cargo_number
        print('cargo number', cargo_number)
                
# =============================================================================
# 
# # =============================================================================
# # dummy
# # =============================================================================
#     def make_dummy(self):
#         pos = np.array((0.03*self.space.x_max,0.03*self.space.y_max))
#         speed = 5
#         destinations = np.array([[self.space.x_max-0.0001,0.03*self.space.y_max], [self.space.x_max*0.03,self.space.y_max-0.0001]])
#         print('destinations dummies', destinations)
#         for i in range(2):
#             destination = destinations[i]
#             dummy_name = i+1
#             print('I am dummy:', dummy_name)
#             print('my destination is:', destination)
#             print('I am agent number:', dummy_name + self.cargo_number + self.n_aircraft + self.n_offloaders + 1 + 1)
#             dummy = Dummy(
#                         dummy_name + self.cargo_number + self.n_aircraft + self.n_offloaders + 1 + 1, # 1xCoordinator and 1x Equipment
#                         self,
#                         pos,
#                         speed,
#                         destination,
#                         dummy_name
#                         )
#                 
#             self.space.place_agent(dummy, pos)
#             self.schedule.add(dummy)
# =============================================================================
    # =========================================================================
    # Define what happens in the model in each step.
    # =========================================================================
    def step(self):
        #all_arrived = True
        if self.schedule.steps == 0:
            self.start_time = time.time()
        
        if self.schedule.steps == self.exit_step:
            self.running = False
        elif self.n_aircraft == self.exited_aircraft:
            if self.exit_step == 1000:
                self.exit_step = self.schedule.steps + 50
                print("--- % s seconds ---" % round(time.time() - self.start_time, 2))
            
            
            

            
        self.schedule.step()
        for agent in self.schedule.agents:
            if type(agent) == Aircraft:
                if agent.aircraft_state == 'Gone':
                    self.space.remove_agent(agent)
                    self.schedule.remove(agent)
                





        # for agent in self.schedule.agents:
        #     if not type(agent) == Aircraft:
        #         self.schedule.step()
        #     elif agent.aircraft_state == 'Gone':
        #         self.space.remove_agent(agent)
        #         self.schedule.remove(agent)
        #     else:
        #         self.schedule.step()
        
        
        
        # self.grid.remove_agent(x)
        # self.schedule.remove(x)
        # self.kill_agents.remove(x)
                    
                    
        
        #self.datacollector.collect(self)