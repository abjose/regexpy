#!/usr/bin/env python


class Metachars:
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
