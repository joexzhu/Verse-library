from functools import reduce
import pickle
from typing import List, Dict, Any, Optional
import json
from treelib import Tree
import numpy.typing as nptyp, numpy as np, portion

from verse.analysis.dryvr import _EPSILON

TraceType = nptyp.NDArray[np.float_]

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
        static = {},
        uncertain_param = {},
        agent={},
        assert_hits={},
        child=[],
        start_time = 0,
        ndigits = 10,
        type = 'simtrace',
        id = 0
    ):
        self.trace: Dict[str, TraceType] = trace
        self.init: Dict[str, List[float]] = init
        self.mode: Dict[str, List[str]] = mode
        self.agent: Dict = agent
        self.child: List[AnalysisTreeNode] = child
        self.start_time: float = round(start_time, ndigits)
        self.assert_hits = assert_hits
        self.type: str = type
        self.static: Dict[str, List[str]] = static
        self.uncertain_param: Dict[str, List[str]] = uncertain_param
        self.id: int = id

    def to_dict(self):
        rst_dict = {
            'id': self.id, 
            'parent': None, 
            'child': [], 
            'agent': {}, 
            'init': {aid: list(init) for aid, init in self.init.items()}, 
            'mode': self.mode, 
            'static': self.static, 
            'start_time': self.start_time,
            'trace': {aid: t.tolist() for aid, t in self.trace.items()}, 
            'type': self.type, 
            'assert_hits': self.assert_hits
        }
        agent_dict = {}
        for agent_id in self.agent:
            agent_dict[agent_id] = f'{type(self.agent[agent_id])}'
        rst_dict['agent'] = agent_dict

        return rst_dict

    def get_track(self, agent_id, D):
        if 'TrackMode' not in self.agent[agent_id].decision_logic.mode_defs:
            return ""
        for d in D:
            if d in self.agent[agent_id].decision_logic.mode_defs['TrackMode'].modes:
                return d
        return ""

    def get_mode(self, agent_id, D):
        res = []
        if 'TrackMode' not in self.agent[agent_id].decision_logic.mode_defs:
            if len(D)==1:
                return D[0]
            return D
        for d in D:
            if d not in self.agent[agent_id].decision_logic.mode_defs['TrackMode'].modes:
                res.append(d)
        if len(res) == 1:
            return res[0]
        else:
            return tuple(res)
            
    @staticmethod
    def from_dict(data) -> "AnalysisTreeNode":
        return AnalysisTreeNode(
            trace = {aid: np.array(data['trace'][aid]) for aid in data["agent"].keys()},
            init = data['init'],
            mode = data['mode'],
            static = data['static'],
            agent = data['agent'],
            assert_hits = data['assert_hits'],
            child = [],
            start_time = data['start_time'],
            type = data['type'],
        )

class AnalysisTree:
    def __init__(self, root):
        self.root:AnalysisTreeNode = root
        self.nodes:List[AnalysisTreeNode] = self.get_all_nodes(root)

    def get_all_nodes(self, root: AnalysisTreeNode) -> List[AnalysisTreeNode]:
        # Perform BFS/DFS to store all the tree node in a list
        res = []
        queue = [root]
        node_id = 0
        while queue:
            node = queue.pop(0)
            # node.id = node_id 
            res.append(node)
            node_id += 1
            queue += node.child
        return res

    def dump(self, fn):
        res_dict = {}
        converted_node = self.root.to_dict()
        res_dict[self.root.id] = converted_node
        queue = [self.root]
        while queue:
            parent_node = queue.pop(0)
            for child_node in parent_node.child:
                node_dict = child_node.to_dict()
                node_dict['parent'] = parent_node.id
                res_dict[child_node.id] = node_dict 
                res_dict[parent_node.id]['child'].append(child_node.id)
                queue.append(child_node)

        with open(fn,'w+') as f:           
            json.dump(res_dict,f, indent=4, sort_keys=True)

    @staticmethod 
    def load(fn):
        f = open(fn, 'r')
        data = json.load(f)
        f.close()
        root_node_dict = data[str(0)]
        root = AnalysisTreeNode.from_dict(root_node_dict)
        queue = [(root_node_dict, root)]
        while queue:
            parent_node_dict, parent_node = queue.pop(0)
            for child_node_idx in parent_node_dict['child']:
                child_node_dict = data[str(child_node_idx)]
                child_node = AnalysisTreeNode.from_dict(child_node_dict)
                parent_node.child.append(child_node)
                queue.append((child_node_dict, child_node))
        return AnalysisTree(root)

    def dump_tree(self):
        tree = Tree()
        AnalysisTree._dump_tree(self.root, tree, 0, 1)
        tree.show()

    @staticmethod
    def _dump_tree(node, tree, pid, id):
        n = "\n".join(str((aid, *node.mode[aid], *node.init[aid])) for aid in node.agent)
        if pid != 0:
            tree.create_node(n, id, parent=pid)
        else:
            tree.create_node(n, id)
        nid = id + 1
        for child in node.child:
            nid = AnalysisTree._dump_tree(child, tree, id, nid)
        return nid + 1

    def contains(self, other: "AnalysisTree", strict: bool = True, tol: Optional[float] = None) -> bool:
        """
        Returns, for reachability, whether the current tree fully contains the other tree or not;
        for simulation, whether the other tree is close enough to the current tree.
        strict: requires set of agents to be the same
        """
        tol = _EPSILON if tol == None else tol
        cur_agents = set(self.nodes[0].agent.keys())
        other_agents = set(other.nodes[0].agent.keys())
        min_agents = list(other_agents)
        types = list(set([n.type for n in self.nodes + other.nodes]))
        assert len(types) == 1, f"Different types of nodes: {types}"
        if not ((strict and cur_agents == other_agents) or (not strict and cur_agents.issuperset(other_agents))):
            return False
        if types[0] == "simtrace":                  # Simulation
            if len(self.nodes) != len(other.nodes):
                return False
            def sim_seg_contains(a: Dict[str, TraceType], b: Dict[str, TraceType]) -> bool:
                return all(a[aid].shape == b[aid].shape and bool(np.all(np.abs(a[aid][:, 1:] - b[aid][:, 1:]) < tol)) for aid in min_agents)
            def sim_node_contains(a: AnalysisTreeNode, b: AnalysisTreeNode) -> bool:
                if not sim_seg_contains(a.trace, b.trace):
                    return False
                if len(a.child) != len(b.child):
                    return False
                child_num = len(a.child)
                other_not_paired = set(range(child_num))
                for i in range(child_num):
                    for j in other_not_paired:
                        if sim_node_contains(a.child[i], b.child[j]):
                            other_not_paired.remove(j)
                            break
                    else:
                        return False
                return True
            return sim_node_contains(self.root, other.root)
        else:                                       # Reachability
            cont_num = len(other.nodes[0].trace[min_agents[0]][0]) - 1
            def collect_ranges(n: AnalysisTreeNode) -> Dict[str, List[List[portion.Interval]]]:
                trace_len = len(n.trace[min_agents[0]])
                cur = {aid: [[portion.closed(n.trace[aid][i][j + 1], n.trace[aid][i + 1][j + 1]) for j in range(cont_num)] for i in range(trace_len)] for aid in min_agents}
                if len(n.child) == 0:
                    return cur
                else:
                    children = [collect_ranges(c) for c in n.child]
                    child_num = len(children)
                    trace_len = len(children[min_agents[0]][0])
                    combined = {aid: [[reduce(portion.Interval.union, (children[i][aid][j][k] for k in range(child_num))) for j in range(cont_num)] for i in range(trace_len)] for aid in other_agents}
                    return {aid: cur[aid] + combined[aid] for aid in other_agents}
            this_tree, other_tree = collect_ranges(self.root), collect_ranges(other.root)
            total_len = len(other_tree[min_agents[0]])
            # bloat and containment
            return all(other_tree[aid][i][j] in this_tree[aid][i][j].apply(lambda x: x.replace(lower=lambda v: v - tol, upper=lambda v: v + tol)) for aid in other_agents for i in range(total_len) for j in range(cont_num))
