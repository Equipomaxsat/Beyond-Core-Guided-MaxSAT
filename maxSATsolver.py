import sys
from tools import unarySoft, maxVar
import math
import time
from collections import defaultdict
from optilog.solvers.sat import Glucose41


class MaxSATsolver:
    def __init__(self, S, H=None, instance="stdin", verbose=False, seed=1, incremental=False):
        if H is None: H = []
        if S is None: S = []
        self.originalvar = max(maxVar(S), maxVar(H))
        self.weight, self.clauses, self.cost = unarySoft(S, H)
        self.lastvar = maxVar(self.clauses)
        self.solver = Glucose41()
        self.solver.add_clauses(self.clauses) 
        self.solver.set("seed", seed)
        self.ubcost = math.inf                         # Minimal cost for all models
        self.time = 0                                  # Time SAT solver is being executed 
        self.unsattime = 0                             # Time SAT solver is executed on unsat calls
        self.numcores = 0                              # Number of times the SAT solver returns False
        self.model = []
        self.instance = instance
        self.verbose = verbose
        self.seed = seed
        self.incremental = incremental
        self.comparators = 0

    def newVar(self):
        self.lastvar += 1
        return self.lastvar

    def getMaxVar(self):
    	return self.lastvar
    	
    def dump(self):
        print("--------------------")
        print("Hard Clauses:")
        print(self.clauses)
        print("Soft Clauses:")
        print(self.weight)
        print("Cost: "+str(self.cost))
        print("Comparators: "+str(self.comparators))
        print("SAT solver time: "+str(self.time))
    	
    def sat(self, assumptions = []):
        t1 = time.process_time()
        x = self.solver.solve(assumptions)
        t = time.process_time() - t1
        self.time += t
        if x == False:
            self.unsattime += t
        print("Instance:", self.instance, "Time:", t, "Answer:", x, "Cost:", self.cost, "Comparators:", self.comparators, "Assumptions:", len(assumptions), file=sys.stderr)
        return x
        
    def add_clauses(self, cls):
        self.clauses += cls
        self.solver.add_clauses(cls)
        
    def restart(self):
        self.solver = Glucose41()
        self.solver.add_clauses(self.clauses)
        self.solver.set("seed", self.seed)
        
    def printresults(self):
        cmd = " ".join(sys.argv).replace(" ", "").replace(self.instance, "")
        print("Method:", cmd, "Instance:", self.instance, "Cost:", self.cost, "Time:", self.time, "UNSATtime:", self.unsattime, "Comparators:", self.comparators, "Cores:",self.numcores)  

