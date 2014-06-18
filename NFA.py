#!/usr/bin/env python
import networkx as nx
import uuid

"""
An NFA consists of:
- A finite set of states Q
- A finite set of input symbols E
- A transition relation R in Q x E x Q
- A start state q_0 in Q
- A set of accepting states F
"""

"""
TODO:
- Could also attempt to make a NFA to DFA converter here
- Also maybe something to trim useless states like from that one article
- Add a function like "unmark_accept_states"...could include an exception list
"""

def uid(self, ):
    return uuid.uuid4()

# actually usually partial NFAs...
class NFA:
    # could make a function map dictionary
    
    def __init__(self, symbol, nfa_list*):
        self.G = nx.DiGraph()
    
    def get_start_states(self, nfa, num_expected=None):
        # probably better way to do this...
        nodes = [g for g,d in nfa.nodes(data=True) if d['start']]
        if num_expected: assert(len(nodes) == num_expected)
        return nodes

    def get_accept_states(self, nfa, num_expected=None):
        # need num_expected?
        nodes = [g for g,d in nfa.nodes(data=True) if d['accept']]
        if num_expected: assert(len(nodes) == num_expected)
        return nodes

    def make_character(self, char):
        n1, n2 = uid(), uid()
        self.G.add_node(n1, start=True, accept=False)
        self.G.add_node(n2, start=False, accept=True)
        self.G.add_edge(n1, n2, label=char)

    def make_union(self, nfa_list):
        assert(len(nfa_list) == 2)
        nfa1, nfa2 = nfa_list
        # copy other NFAs into own graph
        self.G.add_nodes_from(nfa1)
        self.G.add_nodes_from(nfa2)
        # find start and accept states
        start_states = get_start_states(self.G)
        accept_states = get_accept_states(self.G)
        # add new start state and update old ones
        new_start = uid()
        self.G.add_node(new_start, start=True, accept=False)
        for start in start_states:
            self.G.add_edge(new_start, start, label=None)
            self.G.node[start]['start'] = False
        # add new accept state and update old ones
        new_accept = uid()
        self.G.add_node(new_accept, start=False, accept=True)
        for accept in accept_states:
            self.G.add_edge(new_accept, accept, label=None)
            self.G.node[start]['accept'] = False

    def make_concatenation(self, nfa_list):
        assert(len(nfa_list) == 2)
        nfa1, nfa2 = nfa_list
        # new start and accept states
        new_start, new_accept = uid(), uid()
        self.G.add_node(new_start, start=True, accept=False)
        self.G.add_node(new_accept, start=False, accept=True)
        # assume first NFA in list comes first in concatenation
        self.G.add_nodes_from(nfa_list[0])
        # get start and accept states
        start1 = self.get_start_states(nfa1)
        start2 = self.get_start_states(nfa2)
        accept1 = self.get_accept_states(nfa1)
        accept2 = self.get_accept_states(nfa2)
        # connect things
        self.G.add_nodes_from(nfa1)
        self.G.add_nodes_from(nfa2)
        for n in start1:
            self.G.add_edge(new_start, n, label=None)
            self.G.node[n]['start'] = False
        for n in accept2:
            self.G.add_edge(n, new_accept, label=None)
            self.G.node[n]['accept'] = False
        for n1 in accept1:
            for n2 in start2:
                self.G.add_edge(n1, n2, label=None)
                self.G.node[n1]['accept'] = "False"
                self.G.node[n2]['start'] = "False"
        
    def make_kleene(self, nfa_list):
        assert(len(nfa_list) == 1)
        nfa = nfa_list[0]
        # new start and accept states
        new_start, new_accept = uid(), uid()
        self.G.add_node(new_start, start=True, accept=False)
        self.G.add_node(new_accept, start=False, accept=True)
        # also add an edge directly to accept
        self.G.add_edge(new_start, new_accept, label=None)
        # get start, accept states and add nodes from nfa
        start = self.get_start_states(nfa)
        accept = self.get_accept_states(nfa)
        self.G.add_nodes_from(nfa)
        # connect and update nodes
        for n in start:
            self.G.add_edge(new_start, start, label=None)
            self.G.node[start]['start'] = False
        for n in accept:
            # connect old NFA's accept states to new start
            self.G.add_edge(accept new_start, label=None)
            self.G.node[start]['accept'] = False

    def make_plus(self, nfa_list):
        assert(len(nfa_list) == 1)
        nfa = nfa_list[0]
        # new start and accept states, with addition of an intermediate state
        new_start, new_accept, intermediate = uid(), uid(), uid()
        self.G.add_node(new_start, start=True, accept=False)
        self.G.add_node(new_accept, start=False, accept=True)
        self.G.add_node(intermediate, start=False, accept=False)
        # add transition to accept state from intermediate
        self.G.add_edge(intermediate, new_accept, label=None)
        # get accept states and add nodes from nfa
        start = self.get_start_states(nfa)
        accept = self.get_accept_states(nfa)
        self.G.add_nodes_from(nfa)
        # connect and update nodes
        for n in accept:
            self.G.add_edge(n, intermediate, label=None)
            self.G.node[n]['accept'] = False
        for n in start:
            # start states actually stay the same
            self.G.add_edge(intermediate, n, label=None)

    def make_question(self, nfa_list):
        assert(len(nfa_list) == 1)
        nfa = nfa_list[0]
        # new start and accept states
        new_start, new_accept = uid(), uid()
        self.G.add_node(new_start, start=True, accept=False)
        self.G.add_node(new_accept, start=False, accept=True)
        # also add an edge directly to accept
        self.G.add_edge(new_start, new_accept, label=None)
        # get start, accept states and add nodes from nfa
        start = self.get_start_states(nfa)
        accept = self.get_accept_states(nfa)
        self.G.add_nodes_from(nfa)
        # connect and update nodes
        for n in start:
            self.G.add_edge(new_start, n, label=None)
            self.G.node[n]['start'] = False
        for n in accept:
            self.G.add_edge(n, new_accept, label=None)
            self.G.node[n]['accept'] = False
        


if __name__=='__main__':
    pass
