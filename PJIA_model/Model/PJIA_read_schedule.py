
"""
Created on Mon Nov  9 10:34:19 2020

@author: Luka
"""
import pandas as pd
import numpy as np
from ast import literal_eval
from PJIA_model import PJIAModel
#from PJIA_aircraft import Aircraft
taxi = pd.read_excel(r'C:\Users\Luka\OneDrive\Documents\Afstuderen_niet_dropbox\PJIA_model\parking_schedule.xlsx',sheet_name='Sheet2') 

taxi_coordinates_perc = pd.DataFrame.copy(taxi, deep=True)
taxi_coordinates = taxi_coordinates_perc
taxi_coordinates['X_pos'] *= 10
taxi_coordinates['Y_pos'] *= 5
print(taxi_coordinates)

print(taxi_coordinates)
CP_coordinates = np.array([[taxi_coordinates['X_pos'][13], taxi_coordinates['Y_pos'][13]]])
for i in range(14,22):
    print(i)
    coord = [[taxi_coordinates['X_pos'][i], taxi_coordinates['Y_pos'][i]]]
    print(coord)
    CP_coordinates = np.append(CP_coordinates,coord, axis =0)
    
print('cp coordinates:', CP_coordinates)
proberen = CP_coordinates[3:]

print(proberen)

CP_slots = {'CP1' : 'Free', 'CP2': 'Free', 'CP3': 'Free', 'CP4': 'Free', 'CP5': 'Free', 'CP6': 'Free', 'CP7': 'Free', 'CP8': 'Free', 'CP9': 'Free', 'CP10': 'Free'}


route_S1_CP14 = np.array([[taxi_coordinates['X_pos'][0], taxi_coordinates['Y_pos'][0]]])
route_S2_CP14 = np.array([[taxi_coordinates['X_pos'][1], taxi_coordinates['Y_pos'][1]],[taxi_coordinates['X_pos'][0], taxi_coordinates['Y_pos'][0]]])


route_S1_CP56 = np.array([[taxi_coordinates['X_pos'][0], taxi_coordinates['Y_pos'][0]], [taxi_coordinates['X_pos'][1], taxi_coordinates['Y_pos'][1]]])
route_S2_CP56 = np.array([[taxi_coordinates['X_pos'][1], taxi_coordinates['Y_pos'][1]]])

route_S1_CP7 = np.array([[taxi_coordinates['X_pos'][0], taxi_coordinates['Y_pos'][0]], [taxi_coordinates['X_pos'][1], taxi_coordinates['Y_pos'][1]], [taxi_coordinates['X_pos'][2], taxi_coordinates['Y_pos'][2]]])
route_S2_CP7 = np.array([[taxi_coordinates['X_pos'][1], taxi_coordinates['Y_pos'][1]], [taxi_coordinates['X_pos'][2], taxi_coordinates['Y_pos'][2]]])

route_S1_CP8 = np.array([[taxi_coordinates['X_pos'][0], taxi_coordinates['Y_pos'][0]], [taxi_coordinates['X_pos'][1], taxi_coordinates['Y_pos'][1]], [taxi_coordinates['X_pos'][2], taxi_coordinates['Y_pos'][2]], [taxi_coordinates['X_pos'][3], taxi_coordinates['Y_pos'][3]]]) 
route_S2_CP8 = np.array([[taxi_coordinates['X_pos'][1], taxi_coordinates['Y_pos'][1]], [taxi_coordinates['X_pos'][2], taxi_coordinates['Y_pos'][2]], [taxi_coordinates['X_pos'][3], taxi_coordinates['Y_pos'][3]]])

route_S1_CP910 = np.array([[taxi_coordinates['X_pos'][0], taxi_coordinates['Y_pos'][0]], [taxi_coordinates['X_pos'][1], taxi_coordinates['Y_pos'][1]], [taxi_coordinates['X_pos'][2], taxi_coordinates['Y_pos'][2]], [taxi_coordinates['X_pos'][6], taxi_coordinates['Y_pos'][6]]]) 
route_S2_CP910 = np.array([[taxi_coordinates['X_pos'][1], taxi_coordinates['Y_pos'][1]], [taxi_coordinates['X_pos'][2], taxi_coordinates['Y_pos'][2]], [taxi_coordinates['X_pos'][6], taxi_coordinates['Y_pos'][6]]])

# print(route_S1_CP14, route_S2_CP14)
# print(route_S1_CP56, route_S2_CP56)
# print(route_S1_CP7, route_S2_CP7)
# print(route_S1_CP8, route_S2_CP8)
# print(route_S1_CP910, route_S2_CP910)
# destinations = np.array([[x_max,y_min], [x_min,y_max]])
# for i in range(2):
#     print(i)
#     destination = destinations[i]
    
#     print(destination)
    
# taxi = pd.read_excel(r'C:\Users\Luka\OneDrive\Documents\Afstuderen_niet_dropbox\PJIA_model\parking_schedule.xlsx',sheet_name='Sheet2') 
# =============================================================================
# acSchema = pd.read_excel(r'C:\Users\Luka\OneDrive\Documents\Afstuderen_niet_dropbox\PJIA_model\aircraft_schedule.xlsx') 
# taxi = pd.read_excel(r'C:\Users\Luka\OneDrive\Documents\Afstuderen_niet_dropbox\PJIA_model\parking_schedule.xlsx',sheet_name='Sheet4') 
# acSchema = pd.DataFrame.copy(acSchema, deep=True)
# 
# print(acSchema)
# #x = [i for i,l in enumerate(acSchema) if 'A1' in l] 
# # #x = acSchema.Aircraft_ID.eq('A1').index.to_numpy()
# # x = acSchema.index[acSchema.Aircraft_ID == 'A1'][0]
# # y = acSchema.Start_Name[x]
# # xy = len(acSchema)
# print(taxi)
# nodes = np.array([[0.3, 0.02]])
# #for iin in range(xy):
# z = acSchema.Start_Name[2]
# for i in range(len(taxi)-1,-1,-1):
#     if z == taxi.Start[i] and taxi.Parking[i] == 'A':
#         nodes = np.append(nodes, literal_eval(taxi.Nodes[i]), axis=0)
#         print('nodes', nodes)
#         # nodes[:][0] = nodes[:][0]*10
#         # nodes[:][1] *= 5
#         x = nodes[1][0]
#         for item in nodes:
#                                 item[0] *= 5
#                                 item[1] *= 10
#         
#         # for j in range(len(nodes)):
#         #     tussenstap = [nodes[j][0]*10,nodes[j][1]*10]
#         #     nodes_coord.append(tussenstap)
# 
# print('full:', nodes[1:])
# nodes = np.delete(nodes, 0, axis=0)
# #print('delete:', nodes)
# #nodes_coord =  [item[0] for item in nodes] 
# print(nodes)
#    
# 
# =============================================================================

# coordinaten = []
# meer = []
# getal = []
# max_getal = 5

# def probeersel(max_getal):
#     for i in range(max_getal):
#         a = i
#         meer = [a,a]
#         coordinaten.extend(meer)
#         getal.append(i)


    
#     return coordinaten

# print(probeersel(max_getal))

# =============================================================================
# From PJIA_OffloadingAgent, to get the aircraft that is waiting the longest
# =============================================================================
# 
#             for agent in self.model.schedule.agents:
#                 if type(agent) is Aircraft:
#                     waiting_list = []
#                     position_list = []
#                     if agent.aircraft_state == 2:
#
# #                         ### Using Sorted
# #                         get_longest_waiting = itemgetter(0)
# #                         # The parked aircraft with the longest waiting time is the next destination
# #                         
# #                         # save waiting_counter and position
# #                         parked_aircraft.append([agent.waiting_counter, agent.parking_pos])
# #                         
# #                         # destination is position of ac with max waiting time
# #                         parked_aircraft_sorted = sorted(parked_aircraft, key=get_longest_waiting, reverse=True)
# #                         
# #                         destination = parked_aircraft_sorted[0]
# # 
# #                         ### Saving the agent
# #                         parked_aircraft.append(agent)
#                         
#                         
#                         ### Using 2 lists
#                         
#                         waiting_list.append(agent.waiting_counter)
#                         position_list.append(agent.parking_pos)



# =============================================================================
#  From PJIAModel, to randomize positions.
# =============================================================================
            #arrival_time = self.random.uniform(0, self.arrival_window)
            # Starting position
            # pos_x = self.random.uniform(self.origin_x[0],self.origin_x[1]) * self.space.x_max
            # pos_y = self.random.uniform(self.origin_y[0],self.origin_y[1]) * self.space.y_max
            # print(np.array((pos_x,pos_y)))
            #pos = np.array((pos_x,pos_y))
            
            # # Position of parking spot
            # parking_pos_x = self.random.uniform(self.parking_x[0],self.parking_x[1]) * self.space.x_max
            # parking_pos_y = self.random.uniform(self.parking_y[0],self.parking_y[1]) * self.space.y_max
            # parking_pos = np.array((parking_pos_x,parking_pos_y))
            
            # # Position of exit
            # exit_pos_x = self.random.uniform(self.exit_x[0],self.exit_x[1]) * self.space.x_max
            # exit_pos_y = self.random.uniform(self.exit_y[0],self.exit_y[1]) * self.space.y_max
            # exit_pos = np.array((exit_pos_x,exit_pos_y))