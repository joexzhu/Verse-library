from origin_agent import coupled_vanderpol_agent
from verse import Scenario
#from verse.plotter.plotter2D import *
import time

#import plotly.graph_objects as go
from enum import Enum, auto


class AgentMode(Enum):
    Default = auto()


if __name__ == "__main__":
    input_code_name = './demo/dryvr_demo/coupled_vanderpol_controller.py'
    scenario = Scenario()

    car = coupled_vanderpol_agent('car1', file_name=input_code_name)
    scenario.add_agent(car)
    # car = vanderpol_agent('car2', file_name=input_code_name)
    # scenario.add_agent(car)
    # scenario.set_sensor(FakeSensor2())
    # modify mode list input
    scenario.set_init(
        [
            [[1.25, 2.35, 1.25, 2.35,  1], [1.55, 2.45 , 1.55, 2.45, 3]],
            # [[1.55, 2.35], [1.55, 2.35]]
        ],
        [
            tuple([AgentMode.Default]),
            # tuple([AgentMode.Default]),
        ]
    )
    start_time = time.time()

    traces = scenario.verify(
        7, 0.01
    )
    # fig = go.Figure()
    # fig = reachtube_tree(traces, None, fig, 1, 2, [1, 2],
    #                      'lines', 'trace')
    # fig.update_layout(
    #     xaxis_title="x1", yaxis_title="y1"
    # )
    # fig.show()
    # traces = scenario.simulate(7, 0.05)
    # fig = go.Figure()
    # fig = simulation_tree(traces, None, fig, 1, 2, [1, 2],
    #                       'lines', 'trace')
    # fig.show()

    run_time = time.time() - start_time
    print({
        "tool": "verse",
        "benchmark": "CVDP22",
        "setup": "",
        "result": "1",
        "time": run_time,
        "metric2": "",
        "metric3": "",
    })