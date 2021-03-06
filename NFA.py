#!/usr/bin/env python
from metachars import Metachars as M
import matplotlib.pyplot as plt
import networkx as nx
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
- Add a function like "unmark_accept_states"...could include an exception list
- add a copy function that makes new UIDs but preserves data
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
    
    def get_start_states(self, num_expected=None):
        # probably better way to do this...
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
        new_accept, intermediate = uid(), uid()
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
        
    def display(self, title=None):
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
        nx.draw_networkx(self.G, with_labels=False,
                         pos=layout, node_color=ncolors)
        nx.draw_networkx_edge_labels(self.G, pos=layout, edge_labels=elabels,
                                     font_size=20)
        if title: plt.title(title)
        plt.show()

    def remove_extra_epsilons(self, ):
        while self.remove_extra_epsilons_step(): 
            print 'removing empty edges'
            #self.display()

    def remove_extra_epsilons_step(self, ):
        # remove repeated empty transitions
        # find patterns like A-e->B-e->C
        removed = False
        triples = []
        for n in self.G:
            # get all empty edges connected to node n
            # only use pair if one is incoming and one is outgoing
            empty_in  = [(u,v) for u,v in self.G.in_edges(n) 
                         if not self.G[u][v]['label'] and u != v]
            empty_out = [(u,v) for u,v in self.G.out_edges(n) 
                         if not self.G[u][v]['label'] and u != v]
            # get all non-equal pairs (just in case self-loops)
            triples += [(a,b,c) for (a,b) in empty_in for (_,c) in empty_out
                       ]# if a != c] # NEED THIS LAST CLAUSE?

        # for all triples, if they still exist, try a contraction
        for (a,b,c) in triples:
            # verify that this edge hasn't been screwed up
            if not (a in self.G and b in self.G and c in self.G): continue
            if not (self.G.has_edge(a,b) and self.G.has_edge(b,c)): continue
            # make a new empty edge
            self.G.add_edge(a,c, label=None)            
            # copy all data from middle node to first node
            self.G.node[a]['start']  |= self.G.node[b]['start']
            self.G.node[a]['accept'] |= self.G.node[b]['accept']
            for (other,_) in self.G.in_edges(b):
                self.G.add_edge(other,a, label=self.G[other][b]['label'])
            for (_,other) in self.G.out_edges(b):
                self.G.add_edge(a,other, label=self.G[b][other]['label'])
            self.G.remove_node(b)
            removed = True

        return removed

    def remove_dead_ends(self, ):
        # remove non-accept states with only incoming edges
        dead_ends = []
        for n in self.G:
            if len(self.G.out_edges(n)) == 0:
                if not (self.G.node[n]['start'] or self.G.node[n]['accept']):
                    if all([not self.G[u][v]['label'] 
                            for u,v in self.G.in_edges(n)]):
                        # dead end, remove it
                        print "removing dead end"
                        dead_ends.append(n)
        # remove dead ends
        self.G.remove_nodes_from(dead_ends)
                        
    def simulate(self, string):
        # simulate this NFA on a given string
        # list of occupied states - initially list of start states
        occ = set([n for n in self.G if self.G.node[n]['start']])
        # do initial expansion over empty transitions
        occ |= self.take_empty_transitions(occ)
        # iterate over characters in string
        for c in string:
            # follow non-empty transitions
            occ = self.take_symbol_transitions(occ, c)
            # follow empty transitions (repeat until no change)
            occ |= self.take_empty_transitions(occ)
        # check to see if currently in any accept state
        for n in [m for m in self.G if self.G.node[m]['accept']]:
            if n in occ: return True
        return False

    def take_empty_transitions(self, occupied):
        # take all epsilon transitions, return new states
        new_occ = set()
        old_len = -1
        while old_len != len(occupied):
            old_len = len(occupied)
            for n1 in occupied:
                succ = self.G.successors(n1)
                new_occ |= set([n2 for n2 in succ 
                                if not self.G[n1][n2]['label']])
            # update occ
            occupied |= new_occ
        return occupied

    def take_symbol_transitions(self, occupied, symbol):
        # take all relevant symbol transitions, return new states
        new_occ = set()
        for n1 in occupied:
            succ = self.G.successors(n1)
            new_occ |= set([n2 for n2 in succ 
                            if self.G[n1][n2]['label'] == symbol])
        return new_occ

if __name__=='__main__':
    a = NFA('a')
    #a.display(title='a')
    b = NFA('b')
    #b.display(title='b')
    c = NFA('c')
    c.display(title='c')
    c_kleene = NFA('*', c)
    c_kleene.display('c*')
    c_plus = NFA('+', c)
    c_plus.display('c+')
    c_question = NFA('?', c)
    c_question.display('c?')
    a_or_b = NFA('|', a, b)
    a_or_b.display('a|b')
    a_or_b_and_c = NFA('&', a_or_b, c)
    a_or_b_and_c.display('(a|b)c')
    a_or_b_and_c_kleene = NFA('*', a_or_b_and_c)
    a_or_b_and_c_kleene.display('((a|b)c)*')
    a_or_b_and_c_plus = NFA('+', a_or_b_and_c)
    a_or_b_and_c_plus.display('((a|b)c)+')
