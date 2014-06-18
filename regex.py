#!/usr/bin/env python

# Metacharacters. Lower numbers mean lower precedence.
metachars = {'|':0, # union
             '&':1, # concatenation
             # escaped metacharacters go here (same as ampersand)
             '*':2, # match 0 or more times 
             '+':2, # match 1 or more times
             '?':2, # match 0 or 1 times
             '(':3, ')':3, # parens
             '\\':4, # escape...want to use this?
             }

"""
TODO:
- TEST EVERYTHING
- is anything ever right-to-left associative?
"""


def make_concatenation_explicit(regex):
    # make ampersands explicit for convenience
    explicit = ""
    for i in range(1,len(regex)):
        prev = regex[i-1]
        curr = regex[i]
        # if prev and curr are both operands
        if prev not in metachars.keys() and curr not in metachars.keys():
            explicit += '&'
        # if prev is a * or ) and curr is ( or operand
        elif prev in ['*',')'] and (curr=='(' or curr not in metachars.keys()):
            explicit += '&'
        explicit += curr
    return regex[0] + explicit



def infix_to_postfix(regex, verbose=False):
    # Convert passed infix-notation regular expression to postfix notation
    symbols = []
    postfix = ""
    
    i=0
    while i < len(regex): # use while so can try again if need to
        c = regex[i]
        i += 1
        if verbose:
            print "stack:", symbols
            print "output:", postfix
        # print operands as they arrive
        if c not in metachars.keys():
            if verbose: print c,"is an operand"
            postfix += c
        # if stack empty or has left paren on top, push
        elif not symbols or symbols[-1] == '(':
            if verbose: print c,"added to stack because empty or ( on top"
            symbols.append(c)
        # if symbol is a left paren, push
        elif c == '(':
            if verbose: print c,"added to stack because left paren"
            symbols.append(c)
        # if symbol is a right paren, pop until get a left paren
        elif c == ')':
            out = ""
            while out != '(':
                if verbose: print "printing",out,"to get to next left paren"
                postfix += out
                out = symbols.pop()
                # throw an error if run out before encountering left paren?
        # if symbol has higher precedence than top of stack, push
        elif metachars[c] > metachars[symbols[-1]]:
            if verbose: print "putting",c,"on stack because high precedence"
            symbols.append(c)
        # if equal precedence, use associativity
        elif metachars[c] == metachars[symbols[-1]]:
            postfix += symbols.pop()
            if verbose:
                print "printing",postfix[-1],"because equal precedence"
                print "putting",c,"on stack because equal precedence"
            symbols.append(c)
        # if lower precedence, print top operator on stack and try again
        elif metachars[c] < metachars[symbols[-1]]:
            postfix += symbols.pop()
            if verbose:
                print "printing", postfix[-1],"because",c,"is lower precedence"
            i -= 1
        else:
            # something weird happend
            raise Exception("Shouldn't have gotten here.")

    # pop and print everything else (no parens should remain)
    while symbols:
        postfix += symbols.pop()
        if verbose:
            print "adding",postfix[-1],"because done with everything else"
        
    return postfix
        

    


if __name__=="__main__":
    regex = "((a|b)*aba*)*(a|b)(a|b)"
    exp = make_concatenation_explicit(regex)
    post = infix_to_postfix(exp)
    print post
    test = "ab|*a&b&a*&*ab|&ab|&"
    if post == test:
        print "They're equal!"
    else:
        print "They don't match :("

    
