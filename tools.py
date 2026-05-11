import sys
from collections import defaultdict
import math


def maxVar(F):
    """
    Returns the highest variable indef of a formula in any of the mutiple formats.
    """
    if not isinstance(F, list) or len(F) == 0:
        return 0
    
    m = 0
    for C in F:
        if isinstance(C, tuple): #in all cases (weighted SAT clause or XOR clause, the second component is a list of literals
            m = max(m, max(map(abs, C[1]), default=0))
        else:
            m = max(m, max(map(abs, C), default=0))
    return m
 
def foldWCNF(S, H = []):
    """
    Remove duplicated hard clauses and combine soft clauses adding their weights.
    Soft clauses may be a list of literals (with implicit weight one) or a pair weight-clause
    """
    D = defaultdict(int)
    for x in S:
        if isinstance(x, list):
            D[frozenset(x)] += 1
        else:
            D[frozenset(x[1])] += x[0]
    soft = [(w, list(c)) for c, w in D.items()]
    hard = [list(c) for c in {frozenset(c) for c in H}]
    return soft, hard


def Partial_WCNF(S, H = []):
    maxweight = sum([w for w,C in S])
    return S + [(maxweight,C) for C in H]

    
def unarySoft(S, H = []):
    """ 
    Transforms every soft clause to unary (adding hard clauses and fresh variables)
    and represent them by means of a dictionary. In the process, empty clauses may be generated 
    """
    soft, hard = foldWCNF(S,H)
    lastvar =  max(maxVar(S), maxVar(H))
    weight = {}
    cost = 0
    for w, c in soft:
        if len(c) > 1:
            lastvar += 1
            c.append(-lastvar)
            hard.append(c)
            weight[lastvar] = w
        elif len(c) == 0:
            cost += w
        else:
            x = c[0]
            if -x in weight:  # Check if clause was unary and occur with oposite sign
                if w < weight[-x]:
                    weight[-x] -= w
                    cost += w
                else:
                    w2 = weight.pop(-x)
                    cost += w2
                    if w > w2:
                        weight[x] = w - w2
            else:
                if x in weight:
                    weight[x] += w
                else:
                    weight[x] = w
    return weight, hard, cost   

def foldXOR(F):
    """
    Remove duplicated XOR clauses, adding their weights. If two clauses are complementary, replace them by the empty clause
    """
    D = {}   # Dictionary to remove duplicated clauses    
    for w, C, n in F:
        key = (frozenset(C), n)    # Unique identifier for equivalent clauses
        D[key] = D.get(key,0) + w  # Sum weights of equivalent clauses

    cost = 0                       
    R = {}                         # Dictionary to store remanents of complementary clauses
    for (C, n), w1 in D.items():
        if (C, -n) in D and not C in R:
            w2 = D[(C, -n)]
            R[C] = (abs(w1 - w2), n if w1 > w2 else -n)
            cost += min(w1, w2)
    D[(frozenset(), -1)] = D.get((frozenset(), -1), 0) + cost

    foldedF = [(w, list(C), n) for (C, n), w in D.items() if not C in R and w!=0] + [(w, list(C), n) for C, (w,n) in R.items() if w != 0]
    
    return foldedF


def evaluate(F, M):
    """
    Evaluate a XOR or MaxSAT formula formula F on a model M
    """
    cost = 0
    for X in F:
        if isinstance(X, tuple) and len(X)==3:
            prod = 1
            w, C, n = X
            for l in C:
                if -l in M:
                    prod = -prod
            if prod != n:
                cost += w
        else:
            if isinstance(X, list):
                w, C = 1, X
            else:
                w, C = X
            sat = False
            for l in C:
                if l in M:
                    sat = True
                    break
            if not sat:
                cost += w      
    return cost


def printCNF(filename, F):
    if filename is None:
        f = sys.stdout
    else:
        f = open(filename, "w")
    if f.writable():
        # Compact formula

        nvar = maxVar(F)
        ncla = len(F)

        # Write problem line
        f.write(f"p cnf {nvar} {ncla}\n")

        # Write clauses
        for C in F:
            f.write(f" ".join(map(str, C)) + " 0\n")

def printWCNF(filename, S, H = []):
    if filename is None:
        f = sys.stdout
    else:
        f = open(filename, "w")
    if f.writable():
        # Compact formula
        soft, hard = foldWCNF(S, H)
        
        nvar = max(maxVar(soft), maxVar(hard))
        ncla = len(soft) + len(hard)
        mweight = sum(w for w, _ in soft) + 1  # Max weight

        # Write problem line
        f.write(f"p wcnf {nvar} {ncla} {mweight}\n")

        # Write soft clauses
        for w, C in soft:
            f.write(f"{w} " + " ".join(map(str, C)) + " 0\n")

        # Write hard clauses
        for C in hard:
            f.write("h " + " ".join(map(str, C)) + " 0\n")

def printXOR(filename, F):
    if filename is None:
        f = sys.stdout
    else:
        f = open(filename, "w")
    if f.writable():
        # Compact formula
        G = foldXOR(F)
        
        nvar = maxVar(G)
        ncla = len(G)

        # Write problem line
        f.write(f"p xor {nvar} {ncla}\n")

        # Write xor clauses
        for w, C, n in G:
            f.write(f"{w} " + " ".join(map(str, C)) + f" {n}\n")

def readWCNF(filename):
        with open(filename, 'r') as f:
            hard = []
            softs = []
            maxweight = math.inf
            for line in f:
                items = line.split()
                if len(items) == 0 or items[0][0] == "c":
                    continue
                if items[0] == "p":
                    maxweight = int(items[4])
                    continue
                if items[0] != "h" and int(items[0]) <= 0:
                    raise ValueError("Wrong weight")
                if int(items[-1]) != 0:
                    raise ValueError("Clause must end by zero")
                    
                clause = [int (x) for x in items[1:-1]]
                if items[0] == "h" or int(items[0]) >= maxweight:
                    hard.append(clause)
                else:
                    softs.append((int(items[0]), clause))
        return softs, hard

def readXOR(filename):
        with open(filename, 'r') as f:
            G = []
            for line in f:
                items = line.split()
                if len(items) == 0 or items[0] == "c":
                    continue
                if items[0] == "p":
                    continue
                if  int(items[0]) <= 0 and (len(items) > 2 or int(items[1]) != -1):
                    raise ValueError("Only FALSE cosntraint may have negative weight")
                if int(items[-1]) != 1 and int(items[-1]) != -1:
                    raise ValueError("Sign must be 1 or -1")
                    
                C = [int (x) for x in items[1:-1]]
                w = int(items[0])
                n = int(items[-1])
                G.append((w, C, n))
        return G

