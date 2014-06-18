#!/usr/bin/env python
import matplotlib.pyplot as plt
import networkx as nx
from metachars import Metachars as M
import uuid

"""
An NFA consists of:
- A finite set of states Q
- A finite set of input symbols E
- A transition relation R in Q x E x Q
- A start state q_0 in Q
- A set of accepting states F

http://swtch.com/~rsc/regexp/regexp1.html
http://perl.plover.com/Regex/article.html
"""

"""
TODO:
- Could also attempt to make a NFA to DFA converter here
- Also maybe something to trim useless states like from that one article
- Add a function like "unmark_accept_states"...could include an exception list
- add a copy function that makes new UIDs but preserves data
- lots of repeated epsilon edges - problem? could just trim...
"""

def uid():
    return str(uuid.uuid4())

# actually usually partial NFAs...
class NFA:
    # could make a function map dictionary
    
    def __init__(self, symbol, *nfa_list):
        self.G = nx.DiGraph()
        # ehhh, hack
        self.func_mapping = {'|':self.make_union,
                             '&':self.make_concatenation,
                             '*':self.make_kleene,
                             '+':self.make_plus,
                             '?':self.make_question,
                             }
        # operand
        if symbol not in M.metachars.keys():
            self.make_character(symbol, nfa_list)
        elif symbol in self.func_mapping.keys():
            self.func_mapping[symbol](symbol, nfa_list)
        # SHOULD MAKE SYMBOSL AND STUFF FROM regex file available everywhere...
        # just put in a third file and import it I guess
    
    def get_start_states(self, num_expected=None):
        # probably better way to do this...
        #print self.G.nodes(data=True)
        nodes = [g for g,d in self.G.nodes(data=True) if d['start']]
        if num_expected: assert(len(nodes) == num_expected)
        return nodes

    def get_accept_states(self, num_expected=None):
        # need num_expected?
        nodes = [g for g,d in self.G.nodes(data=True) if d['accept']]
        if num_expected: assert(len(nodes) == num_expected)
        return nodes

    def make_character(self, symbol, nfa_list):
        n1, n2 = uid(), uid()
        self.G.add_node(n1, start=True, accept=False)
        self.G.add_node(n2, start=False, accept=True)
        self.G.add_edge(n1, n2, label=symbol)

    def make_union(self, symbol, nfa_list):
        assert(len(nfa_list) == 2)
        nfa1, nfa2 = nfa_list
        # copy other NFAs into own graph
        self.G.add_nodes_from(nfa1.G.nodes(data=True))
        self.G.add_nodes_from(nfa2.G.nodes(data=True))
        self.G.add_edges_from(nfa1.G.edges(data=True))
        self.G.add_edges_from(nfa2.G.edges(data=True))
        # find start and accept states
        start = self.get_start_states()
        accept = self.get_accept_states()
        # add new start state and update old ones
        new_start = uid()
        self.G.add_node(new_start, start=True, accept=False)
        for n in start:
            self.G.add_edge(new_start, n, label=None)
            self.G.node[n]['start'] = False
        # add new accept state and update old ones
        new_accept = uid()
        self.G.add_node(new_accept, start=False, accept=True)
        for n in accept:
            self.G.add_edge(n, new_accept, label=None)
            self.G.node[n]['accept'] = False

    def make_concatenation(self, symbol, nfa_list):
        assert(len(nfa_list) == 2)
        # assume first NFA in list comes first in concatenation
        nfa1, nfa2 = nfa_list
        # new start and accept states
        new_start, new_accept = uid(), uid()
        self.G.add_node(new_start, start=True, accept=False)
        self.G.add_node(new_accept, start=False, accept=True)
        # get start and accept states
        start1 = nfa1.get_start_states()
        start2 = nfa2.get_start_states()
        accept1 = nfa1.get_accept_states()
        accept2 = nfa2.get_accept_states()
        # connect things
        self.G.add_nodes_from(nfa1.G.nodes(data=True))
        self.G.add_nodes_from(nfa2.G.nodes(data=True))
        self.G.add_edges_from(nfa1.G.edges(data=True))
        self.G.add_edges_from(nfa2.G.edges(data=True))
        # connect new start to nfa1's starts
        for n in start1:
            self.G.add_edge(new_start, n, label=None)
            self.G.node[n]['start'] = False
        # connect nfa2's accepts to new accepts
        for n in accept2:
            self.G.add_edge(n, new_accept, label=None)
            self.G.node[n]['accept'] = False
        # connect nfa1's accepts to nfa2's starts
        for n1 in accept1:
            for n2 in start2:
                self.G.add_edge(n1, n2, label=None)
                self.G.node[n1]['accept'] = False
                self.G.node[n2]['start'] = False

    def make_kleene(self, symbol, nfa_list):
        assert(len(nfa_list) == 1)
        nfa = nfa_list[0]
        # new start and accept states
        new_start, new_accept = uid(), uid()
        self.G.add_node(new_start, start=True, accept=False)
        self.G.add_node(new_accept, start=False, accept=True)
        # also add an edge directly to accept
        self.G.add_edge(new_start, new_accept, label=None)
        # get start, accept states and add nodes from nfa
        start = nfa.get_start_states()
        accept = nfa.get_accept_states()
        self.G.add_nodes_from(nfa.G.nodes(data=True))
        self.G.add_edges_from(nfa.G.edges(data=True))
        # connect and update nodes
        for n in start:
            self.G.add_edge(new_start, n, label=None)
            self.G.node[n]['start'] = False
        for n in accept:
            # connect old NFA's accept states to new start
            self.G.add_edge(n, new_start, label=None)
            self.G.node[n]['accept'] = False

    def make_plus(self, symbol, nfa_list):
        assert(len(nfa_list) == 1)
        nfa = nfa_list[0]
        # new start and accpt states, with addition of an intermediate state
        #new_start, new_accept, intermediate = uid(), uid(), uid()
        new_accept, intermediate = uid(), uid()
        #self.G.add_node(new_start, start=True, accept=False)
        self.G.add_node(new_accept, start=False, accept=True)
        self.G.add_node(intermediate, start=False, accept=False)
        # add transition to accept state from intermediate
        self.G.add_edge(intermediate, new_accept, label=None)
        # get accept states and add nodes from nfa
        start = nfa.get_start_states()
        accept = nfa.get_accept_states()
        self.G.add_nodes_from(nfa.G.nodes(data=True))
        self.G.add_edges_from(nfa.G.edges(data=True))
        # connect and update nodes
        for n in accept:
            self.G.add_edge(n, intermediate, label=None)
            self.G.node[n]['accept'] = False
        for n in start:
            # start states actually stay the same
            self.G.add_edge(intermediate, n, label=None)

    def make_question(self, symbol, nfa_list):
        assert(len(nfa_list) == 1)
        nfa = nfa_list[0]
        # new start and accept states
        new_start, new_accept = uid(), uid()
        self.G.add_node(new_start, start=True, accept=False)
        self.G.add_node(new_accept, start=False, accept=True)
        # also add an edge directly to accept
        self.G.add_edge(new_start, new_accept, label=None)
        # get start, accept states and add nodes from nfa
        start = nfa.get_start_states()
        accept = nfa.get_accept_states()
        self.G.add_nodes_from(nfa.G.nodes(data=True))
        self.G.add_edges_from(nfa.G.edges(data=True))
        # connect and update nodes
        for n in start:
            self.G.add_edge(new_start, n, label=None)
            self.G.node[n]['start'] = False
        for n in accept:
            self.G.add_edge(n, new_accept, label=None)
            self.G.node[n]['accept'] = False
        
    def display(self):
        # should hide names but show start and accept nodes differently
        # also show edge labels
        ncolors = []
        for n in self.G:
            if self.G.node[n]['start']:
                ncolors.append('green')
            elif self.G.node[n]['accept']:
                ncolors.append('red')
            else:
                ncolors.append('blue')
        elabels = dict()
        for p,s in self.G.edges():
            lbl = self.G.edge[p][s]['label']
            if lbl != None: elabels[(p,s)] = r'$'+lbl+'$'
            else: elabels[(p,s)] = r'$\epsilon$'
        layout = nx.graphviz_layout(self.G)
        nx.draw_networkx(self.G, with_labels=False, pos=layout,
                         node_color=ncolors)
        nx.draw_networkx_edge_labels(self.G, pos=layout, edge_labels=elabels,
                                     font_size=20)
        plt.show()

    def remove_extra_epsilons(self, ):
        # remove repeated empty transitions
        # find patterns like A-e->B-e->C
        pairs = []
        for n in self.G:
            # get all empty edges connected to node n
            # only use pair if one is incoming and one is outgoing
            empty_in  = [(u,v) for u,v in self.G.in_edges() 
                         if not self.G[u][v][label]]
            empty_out = [(u,v) for u,v in self.G.out_edges() 
                         if not self.G[u][v][label]]
            # get all non-equal pairs
            pairs += [(i,o) for i in empty_in for o in empty_out]
        # for all triples, if they still exist, try a contraction
        for (i1, o1),(i2,o2) in pairs:
            # make a new empty edge
            # o1 and i2 are the same, i1 is pred, o2 is succ
            self.G.add_edge(i1, o2, label=None)
            # if middle node has no other edges, remove
            if self.G.degree(o1) == 2: self.G.remove_node(o1)
            # otherwise just remove the edges
            else: self.G.remove_edges_from([(i1,o1), (i2,o2)])
            

if __name__=='__main__':
    a = NFA('a')
    b = NFA('b')
    c = NFA('c')
    c_kleene = NFA('*', c)
    c_plus = NFA('+', c)
    c_question = NFA('?', c)
    a_or_b = NFA('|', a, b)
    a_or_b_and_c = NFA('&', a_or_b, c)
    a_or_b_and_c_kleene = NFA('*', a_or_b_and_c)
    a_or_b_and_c_plus = NFA('+', a_or_b_and_c)
    a_or_b_and_c_plus.display()
