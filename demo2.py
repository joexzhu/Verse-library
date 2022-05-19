from src.example.example_agent.car_agent import CarAgent, NPCAgent
from src.scene_verifier.scenario.scenario import Scenario
from src.example.example_map.simple_map2 import SimpleMap2, SimpleMap3, SimpleMap5, SimpleMap6
from src.plotter.plotter2D import *
from src.example.example_sensor.fake_sensor import FakeSensor2

import matplotlib.pyplot as plt
import numpy as np
from enum import Enum, auto

class VehicleMode(Enum):
    Normal = auto()
    SwitchLeft = auto()
    SwitchRight = auto()
    Brake = auto()

class LaneMode(Enum):
    Lane0 = auto()
    Lane1 = auto()
    Lane2 = auto()

class State:
    x = 0.0
    y = 0.0
    theta = 0.0
    v = 0.0
    vehicle_mode: VehicleMode = VehicleMode.Normal
    lane_mode: LaneMode = LaneMode.Lane0

    def __init__(self, x, y, theta, v, vehicle_mode: VehicleMode, lane_mode: LaneMode):
        self.data = []

if __name__ == "__main__":
    input_code_name = 'example_controller2.py'
    scenario = Scenario()

    car = NPCAgent('car1', file_name=input_code_name)
    scenario.add_agent(car)
    car = CarAgent('car2', file_name=input_code_name)
    scenario.add_agent(car)
    tmp_map = SimpleMap3()
    scenario.set_map(tmp_map)
    scenario.set_sensor(FakeSensor2())
    scenario.set_init(
        [
            [[20, 0, 0, 0.5],[20, 0, 0, 0.5]], 
            [[15, -0.2, 0, 2.0],[16.0, 0.2, 0, 3.0]],
        ],
        [
            (VehicleMode.Normal, LaneMode.Lane1),
            (VehicleMode.Normal, LaneMode.Lane1),
        ]
    )
    res_list = scenario.simulate_multi(10,10)
    # traces = scenario.verify(10)

    fig = plt.figure(2)
    # fig,x_lim,y_lim = plot_map(tmp_map, 'g', fig)
    # fig,x_lim,y_lim = plot_reachtube_tree(traces, 'car1', 0, [1], 'b', fig)
    # fig,x_lim,y_lim = plot_reachtube_tree(traces, 'car2', 0, [1], 'r', fig,x_lim,y_lim)
    for traces in res_list:
        fig,x_lim,y_lim = plot_simulation_tree(traces, 'car1', 0, [1], 'b', fig)
        fig,x_lim,y_lim = plot_simulation_tree(traces, 'car2', 0, [1], 'r', fig, x_lim, y_lim)


    plt.show()