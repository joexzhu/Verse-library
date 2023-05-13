import functools, pprint, random, math
from typing import Dict, Optional, Tuple
from verse.agents.example_agent import CarAgentDebounced
from verse.analysis.analysis_tree import AnalysisTree, first_transitions
from verse.analysis.utils import wrap_to_pi
from verse.map.example_map.intersection import Intersection
from verse.scenario.scenario import Benchmark, Scenario
pp = functools.partial(pprint.pprint, compact=True, width=130)

from controller.intersection_car import AgentMode

JERK = 0
CAR_NUM = 6
LANES = 3
CAR_ACCEL_RANGE = (0.7, 3)
CAR_SPEED_RANGE = (1, 3)
CAR_THETA_RANGE = (-0.1, 0.1)
RUN_TIME = 20 #old value 60

class ArgumentDict:
    def __init__(self):
        self.dict_internal = {}
    def add(self, key, value):
        self.dict_internal[key] = value
    def get(self, key, default_value:any=None):
        return self.dict_internal[key] if key in self.dict_internal.keys() else (eval(default_value) if default_value is not None else None)

def first_transitions(tree: AnalysisTree) -> Dict[str, float]:     # id, start time
    d = {}
    for node in tree.nodes:
        for child in node.child:
            for aid in node.agent:
                if aid not in d and node.mode[aid] != child.mode[aid]:
                    d[aid] = child.start_time
    return d

def rand(start: float, end: float) -> float:
    return random.random() * (end - start) + start

def run(meas=False):
    if bench.config.sim:
        bench.scenario.simulator.cache_hits = (0, 0)
    else:
        bench.scenario.verifier.tube_cache_hits = (0, 0)
        bench.scenario.verifier.trans_cache_hits = (0, 0)
    if not meas and not bench.scenario.config.incremental:
        return
    traces = bench.run(RUN_TIME, 0.05)

    if bench.config.dump:
        traces.dump("tree2.json" if meas else "tree1.json") 

    if bench.config.plot:
        import plotly.graph_objects as go
        from verse.plotter.plotter2D import reachtube_tree, simulation_tree

        fig = go.Figure()
        if bench.config.sim:
            fig = simulation_tree(traces, bench.scenario.map, fig, 1, 2, print_dim_list=[1, 2])
        else:
            fig = reachtube_tree(traces, bench.scenario.map, fig, 1, 2, [1, 2], 'lines',combine_rect=5)
        fig.show()

    if meas:
        bench.report()
    print(f"agent transition times: {first_transitions(traces)}")

if __name__ == "__main__":
    import sys
    bench = Benchmark(sys.argv)
    ctlr_src = "demo/vehicle/controller/intersection_car.py"
    alt_ctlr_src = ctlr_src.replace(".py", "_sw5.py") 
    import time
    
    arg_dict = ArgumentDict()
    for i in range(1, len(sys.argv)):
        key_value = sys.argv[i].split('=')
        if len(key_value) == 2:
            key, value = key_value
            arg_dict.add(key.upper(), value.upper())
    
    CAR_NUM = int(arg_dict.get("CAR_NUM", '9'))
    LANES = int(arg_dict.get("LANES", '4'))
    seed = int(arg_dict.get("SEED", "time.time()"))
    RUN_TIME = int(arg_dict.get("RUN_TIME", "40"))
    CAR_ID = int(arg_dict.get("CAR_ID", "-1"))
    #OUTPUT_FILENAME = arg_dict.get("OUTPUT")
    
    # if len(sys.argv) >= 3:
    #     seed = int(sys.argv[2])
    # else:
    #     seed = int(time.time())

    # if len(sys.argv) == 5:
    #     CAR_NUM = int(sys.argv[3])
    #     LANES = int(sys.argv[4])

    print()
    print("---------------  ", sys.argv[1], "  ---------------")
    print(f"seed: {seed}, LANES: {LANES}, CAR_NUM: {CAR_NUM}, runtime: {RUN_TIME}, CAR_ID: {CAR_ID}")
    random.seed(seed)

    dirs = "WSEN"
    LANES = int(sys.argv[3])
    CAR_NUM = int(sys.argv[4])
    map = Intersection(lanes=LANES, length=400)
    bench.scenario.set_map(map)
    def set_init(id: str, alt_pos: Optional[Tuple[float, float]] = None):
        dir = random.randint(0, 3)
        src = dirs[dir]
        dst_dirs = list(dirs)
        dst_dirs.remove(src)
        dst = dst_dirs[random.randint(0, 2)]
        mid_lane_ind = int(map.lanes / 2 - 1)
        lane = random.randint(mid_lane_ind, mid_lane_ind + 1)
        start, off = (map.size + rand(0, map.length * 0.3), rand(0, map.width) + map.width * lane)
        pos = { "N": (-off, start), "S": (off, -start), "W": (-start, -off), "E": (start, off) }[src] if alt_pos == None else alt_pos
        init = [*pos, *((wrap_to_pi(dir * math.pi / 2 + rand(*CAR_THETA_RANGE)), rand(*CAR_SPEED_RANGE)) if alt_pos == None else bench.scenario.init_dict[id][0][2:4]), 0]
        assert len(init) == 5, bench.scenario.init_dict
        modes = (AgentMode.Accel, f"{src}{dst}_{lane}") if alt_pos == None else bench.scenario.init_mode_dict[id]
        if not bench.config.sim:
            def j(st, s):
                return [st[0] + s * JERK, st[1] + s * JERK, *st[2:]]
            bench.scenario.set_init_single(id, (j(init, -1), j(init, 1)), modes)
        else:
            bench.scenario.set_init_single(id, (init,), modes)
    car_id = lambda i: f"car{i}"

    for i in range(CAR_NUM):
        car = CarAgentDebounced(car_id(i), file_name=ctlr_src, speed=rand(*CAR_SPEED_RANGE), accel=rand(*CAR_ACCEL_RANGE))
        bench.scenario.add_agent(car)
        set_init(car.id)

    print(f'bench.config.args: {bench.config.args}')
    if 'b' in bench.config.args:
        run(True)
    elif 'r' in bench.config.args:
        run()
        run(True)
    elif 'n' in bench.config.args:
        run()
        set_init(car_id(CAR_ID), (100, -0.8))
        run(True)
    #elif '3' in bench.config.args:
        # run()
        # old_agent = bench.scenario.agent_dict["car3"]
        # bench.scenario.agent_dict["car3"] = CarAgentDebounced('car3', file_name=ctlr_src.replace(".py", "_sw5.py"),
        #                                                       speed=old_agent.speed, accel=old_agent.accel)
        # run(True)

    elif CAR_ID >= 0: 
        if bench.scenario.config.incremental:    # only run for incremental
            run()
        car = f"car{CAR_ID}"
        old_agent = bench.scenario.agent_dict[car]
        bench.scenario.agent_dict[car] = CarAgentDebounced(car, file_name=ctlr_src.replace(".py", "_sw5.py"),
                                                              speed=old_agent.speed, accel=old_agent.accel)
        run(True)
    
    
    print(f"seed: {seed} \tcar_id: {CAR_ID}")
    print(bench.scenario.verifier.tube_cache_hits, bench.scenario.verifier.trans_cache_hits)
    # if 'l' in sys.argv[1] and 'v' in sys.argv[1]:
    #     import ray
    #     import datetime
    #     ray.timeline(OUTPUT_FILENAME + datetime.datetime.now().strftime("%m%d-%H%M%S") + ".txt")
