import numpy as np
from mesa import Agent


class Cargo(Agent):
    
    # =========================================================================
    # Create a new Equipment agent
    #
    # Args:
    #     unique_id: Unique agent identifier.
    #     pos: Starting position
    #     schedule_ID: ID of the aircraft in the schedule, where the cargo belongs to
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
    
        
        # Cargo states:
        #   aircraft
        #   equipment/offloader
        #   building
        #   interacting
        


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
     
        