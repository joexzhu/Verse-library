from typing import List, Dict

class AnalysisTreeNode:
    """AnalysisTreeNode class
    A AnalysisTreeNode stores the continous execution of the system without transition happening"""
    trace: Dict
    """The trace for each agent. 
    The key of the dict is the agent id and the value of the dict is simulated traces for each agent"""
    init: Dict 
    
    def __init__(
        self,
        trace={},
        init={},
        mode={},
        agent={},
        child=[],
        start_time = 0,
        ndigits = 10,
        type = 'simtrace'
    ):
        self.trace:Dict = trace
        self.init:Dict = init
        self.mode:Dict = mode
        self.agent:Dict = agent
        self.child:List[AnalysisTreeNode] = child
        self.start_time:float = round(start_time,ndigits)
        self.type:str = type