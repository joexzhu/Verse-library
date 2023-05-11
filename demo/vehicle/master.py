import functools, pprint, random, math
import ray
from demo.vehicle.intersection import ArgumentDict
from verse.agents.example_agent import CarAgentDebounced
from verse.analysis.utils import wrap_to_pi
from verse.map.example_map.intersection import Intersection
from verse.scenario.scenario import Benchmark

pp = functools.partial(pprint.pprint, compact=True, width=130)

from controller.intersection_car import AgentMode
import datetime
import subprocess
import os, sys

if __name__ == "__main__":
    arg_dict = ArgumentDict()
    for i in range(1, len(sys.argv)):
        key_value = sys.argv[i].split('=')
        if len(key_value) == 2:
            key, value = key_value
            arg_dict.add(key.upper(), value.upper())
    APP_NAME = str(arg_dict.get('APP', 'INTERSECTION')).upper()
    
    # output = sys.stdout
    RANDOM_SEED = 1118    #460, 1118, 1682538796
    LANES_LIST = [4]
    CAR_LIST = [15]
    RUN_TIME_LIST =[30]
    RUN_MODE_LIST = ['vl'] 
    # ['bv','blv'] for multiple cores + incemental exploring #???collect setup: b, 3+[i]+[l]
    # ['vl', 'vli', 'vi', 'v'] for incremental
    # ['vrli'] for repeat
    RUN_OPTION = ['1', '2', 'n', '']
    CAR_ID_LIST = [8]#[6, 5, 8] # used for changing decision logic
    # -1 as the 1st element in the list means no need to change decision logic. can be used to explore transition times
    # some useful transition times
    # {'car5': 1.0, 'car8': 14.6, 'car9': 46.6, 'car6': 48.6}
    # {'car3': 1.0, 'car5': 1.0, 'car24': 12.6, 'car8': 14.6, 'car21': 16.1, 'car19': 39.35}
    OUTPUT_FILENAME = f"output-experiments(0511)-{APP_NAME}" + ".txt"
    alt_car_list = []
    
    # First check how many CPU is online
    with open(OUTPUT_FILENAME, "a") as f:
        print(file=f)
        print(f"=============={APP_NAME}==============", file=f)
        
    output=open(OUTPUT_FILENAME, "a")
    subprocess.call(["grep", "processor", "/proc/cpuinfo"], stdout=output, stderr=output)
    
    my_env = os.environ.copy()
    # my_env["RAY_PROFILING"] = "1"

    if APP_NAME == 'INTERSECTION':
        for LANE in LANES_LIST:
            # if LANE == 4:
            #     CAR_LIST = [15]
            #     RUN_TIME_LIST =[18, 20]
            #     CAR_ID_LIST = [8]
            # else:
            #     CAR_LIST = [25]
            #     RUN_TIME_LIST =[10, 13, 20]
            #     CAR_ID_LIST = [24]
            for car in CAR_LIST:
                for run_time in RUN_TIME_LIST:
                    for car_id in CAR_ID_LIST:
                        for run_mode in RUN_MODE_LIST:
                            print(f'{datetime.datetime.now()}----->>>>>{APP_NAME}-{run_mode}', file=open(OUTPUT_FILENAME, "a"))
                            # print(LANE, car, run_time, car_id, run_mode)
                            subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection.py", run_mode, 
                                             f"SEED={RANDOM_SEED}", f"LANES={LANE}", f"CAR_NUM={car}",  
                                             f"RUN_TIME={run_time}", f"CAR_ID={car_id}", 
                                             f"OUTPUT={OUTPUT_FILENAME}"], stdout=output, stderr=output, env=my_env)
                        if car_id == -1:
                            break
    elif APP_NAME == 'GEARBOX':
        RUN_OPTION = ['1', 'n', '']
        for run_option in RUN_OPTION:
            for run_mode in RUN_MODE_LIST:
                print(f'{datetime.datetime.now()}----->>>>>{APP_NAME}-{run_mode}{run_option}', file=open(OUTPUT_FILENAME, "a"))
                subprocess.call(["/usr/bin/time", "-v", "python", "demo/tacas2023/exp12/gearbox_demo.py", run_mode + run_option, 
                                f"OUTPUT={OUTPUT_FILENAME}"], stdout=output, stderr=output, env=my_env)
    elif APP_NAME == 'THERMO':
        for run_option in RUN_OPTION:
            for run_mode in RUN_MODE_LIST:
                print(f'{datetime.datetime.now()}----->>>>>{APP_NAME}-{run_mode}{run_option}', file=open(OUTPUT_FILENAME, "a"))
                subprocess.call(["/usr/bin/time", "-v", "python", "demo/dryvr_demo/adv_thermo_demo.py", run_mode + run_option, 
                                f"OUTPUT={OUTPUT_FILENAME}"], stdout=output, stderr=output, env=my_env)
    elif APP_NAME == 'EXP10':
        for run_option in RUN_OPTION:
            for run_mode in RUN_MODE_LIST:
                print(f'{datetime.datetime.now()}----->>>>>{APP_NAME}-{run_mode}{run_option}', file=open(OUTPUT_FILENAME, "a"))
                subprocess.call(["/usr/bin/time", "-v", "python", "demo/tacas2023/exp10/exp10_dryvr.py", run_mode + run_option, 
                                f"OUTPUT={OUTPUT_FILENAME}"], stdout=output, stderr=output, env=my_env)
    elif APP_NAME == 'INC-EXPR':
        for run_option in RUN_OPTION:
            for run_mode in RUN_MODE_LIST:
                print(f'{datetime.datetime.now()}----->>>>>{APP_NAME}-{run_mode}{run_option}', file=open(OUTPUT_FILENAME, "a"))
                subprocess.call(["/usr/bin/time", "-v", "python", "demo/tacas2023/exp11/inc-expr.py", run_mode + run_option, 
                                f"OUTPUT={OUTPUT_FILENAME}"], stdout=output, stderr=output, env=my_env)

    print(datetime.datetime.now(), file=open(OUTPUT_FILENAME, "a"))
    
    '''
    verify_incrmental
    x_list = [77.09140887861837, 80, 85, 100, 120, 150]
    y_list = [9, 10, 10.5, 11, 11.619671922657663]
    start:106.07500751049828, off: 2.5459862275151646
    x_list = [100]
    y_list = [3]
    subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection_inc.py", "in", str(RANDOM_SEED), str(CAR_NUM), str(LANES), str(alt_car_list) ], stdout=output, stderr=output)


    for i in [0, 2, 4, 6]:
        alt_car_list = [i]
        subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection_inc.py", "in", str(RANDOM_SEED), str(CAR_NUM), str(LANES), str(alt_car_list) ], stdout=output, stderr=output)

    for i1 in [1, 3 ]:
        for i2 in [5, 7]:
            alt_car_list = [i1, i2]
            subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection_inc.py", "in", str(RANDOM_SEED), str(CAR_NUM), str(LANES), str(alt_car_list) ], stdout=output, stderr=output)

    for i1 in [0]:
        for i2 in [2, 4]:
            for i3 in [6, 8]:
                alt_car_list = [i1, i2, i3]
                subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection_inc.py", "in", str(RANDOM_SEED), str(CAR_NUM), str(LANES), str(alt_car_list) ], stdout=output, stderr=output)

    for i1 in [1, 3]:
        for i2 in [4, 6]:
            for i3 in [7]:
                for i4 in [8]:
                    alt_car_list = [i1, i2, i3, i4]
                    subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection_inc.py", "in", str(RANDOM_SEED), str(CAR_NUM), str(LANES), str(alt_car_list) ], stdout=output, stderr=output)

    for i1 in [0]:
        for i2 in [2]:
            for i3 in [4]:
                for i4 in [5, 6]:
                    for i5 in [7, 8]:
                        alt_car_list = [i1, i2, i3, i4, i5]
                        subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection_inc.py", "in", str(RANDOM_SEED), str(CAR_NUM), str(LANES), str(alt_car_list) ], stdout=output, stderr=output)

    for i1 in [0]:
        for i2 in [1]:
            for i3 in [2, 3]:
                for i4 in [4, 5]:
                    for i5 in [7]:
                        for i6 in [8]:
                            alt_car_list = [i1, i2, i3, i4, i5, i6]
                            subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection_inc.py", "in", str(RANDOM_SEED), str(CAR_NUM), str(LANES), str(alt_car_list) ], stdout=output, stderr=output)

    for i1 in [0, 1]:
        for i2 in [2]:
            for i3 in [3]:
                for i4 in [4]:
                    for i5 in [5]:
                        for i6 in [6]:
                            for i7 in [7, 8]:
                                alt_car_list = [i1, i2, i3, i4, i5, i6, i7]
                                subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection_inc.py", "in", str(RANDOM_SEED), str(CAR_NUM), str(LANES), str(alt_car_list) ], stdout=output, stderr=output)

    for i1 in [0, 1]:
        for i2 in [2]:
            for i3 in [3]:
                for i4 in [4]:
                    for i5 in [5]:
                        for i6 in [6]:
                            for i7 in [7]:
                                for i8 in [8]:
                                    alt_car_list = [i1, i2, i3, i4, i5, i6, i7, i8]
                                    subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection_inc.py", "in", str(RANDOM_SEED), str(CAR_NUM), str(LANES), str(alt_car_list) ], stdout=output, stderr=output)

    alt_car_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection_inc.py", "in", str(RANDOM_SEED), str(CAR_NUM), str(LANES), str(alt_car_list) ], stdout=output, stderr=output)
    # for x in x_list:
    #     for y in y_list:
    #         subprocess.call(["/usr/bin/time", "-v", "python", "demo/vehicle/intersection_inc.py", "inv", str(RANDOM_SEED), str(CAR_NUM), str(LANES), str(x), str(y) ], stdout=output, stderr=output)
    print(time.time)
    '''