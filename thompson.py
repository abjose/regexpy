#!/usr/bin/env python
from regex import infix_to_postfix
from NFA import NFA

# implementation of Thompson's Algorithm for regex to NFA conversion
# references:
# http://ezekiel.vancouver.wsu.edu/~cs317/archive/projects/grep/grep.pdf


def regex_to_NFA(regex):
    # convert infix regex to NFA
    # first change regex as passed (infix) to postfix
    regex = infix_to_postfix(regex)
    # stack for pushing NFAs onto while going through string
    nfa_stack = []
    
    i = 0
    while i < len(regex): # again, use while because might have to back up
        c = regex[i]
        i += 1
        #if c == '\\': # escape character - see if next character is metachar
        #if c == '.':  # wildcard
        if c == '&':
            nfa2 = nfa_stack.pop()
            nfa1 = nfa_stack.pop()
            nfa_stack.append(NFA('&', nfa1, nfa2))
        elif c == '|':
            nfa2 = nfa_stack.pop()
            nfa1 = nfa_stack.pop()
            nfa_stack.append(NFA('|', nfa1, nfa2))
        elif c == '*':
            nfa = nfa_stack.pop()
            nfa_stack.append(NFA('*', nfa))
        elif c == '+':
            nfa = nfa_stack.pop()
            nfa_stack.append(NFA('+', nfa))
        elif c == '?':
            nfa = nfa_stack.pop()
            nfa_stack.append(NFA('?', nfa))
        else:
            # must be a character
            nfa_stack.append(NFA(c))

    assert(len(nfa_stack) == 1)
    return nfa_stack[0]


if __name__=='__main__':
    test = "((a|b)*aba*)*(a|b)(a|b)"
    #test = 'abc'
    nfa = regex_to_NFA(test)
    #nfa.display()
    nfa.remove_extra_epsilons()
    #nfa.display()
    nfa.remove_dead_ends()
    #nfa.display()
    print nfa.simulate('bbabaaaa')
    nfa.display()
