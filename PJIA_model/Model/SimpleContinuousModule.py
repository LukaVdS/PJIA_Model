"""
Created on Tue Sep  8 13:39:52 2020

@author: Luka
"""
from mesa.visualization.ModularVisualization import VisualizationElement


class SimpleCanvas(VisualizationElement):
    local_includes = ["Model/simple_continuous_canvas.js"] # why need to keep the 'boid_flockers/'part?
    portrayal_method = None
    canvas_height = 800 #starting values?
    canvas_width = 800*480./1100

    def __init__(self, portrayal_method, canvas_width=1000, canvas_height=1000*480./1100):
        """
        Instantiate a SimpleCanvas
        """
        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = "new Simple_Continuous_Module({}, {})".format(
            self.canvas_width, self.canvas_height
        )
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        space_state = []
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            x, y = obj.pos
            x = (x - model.space.x_min) / (model.space.x_max - model.space.x_min)
            y = (y - model.space.y_min) / (model.space.y_max - model.space.y_min)
            portrayal["x"] = x
            portrayal["y"] = y
            space_state.append(portrayal)
        return space_state

