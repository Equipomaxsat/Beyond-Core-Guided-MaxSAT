import sys
import argparse
import math
from maxSATsolver import MaxSATsolver
from cardinality import sortingNetwork
from tools import readWCNF
        
        
class FuMalik(MaxSATsolver):

    def __init__(self, S, H=None, instance="stdin", verbose=False, seed=1, incremental=False):
        if incremental:
            raise ValueError("Algorithm does not work in incremental mode")
        super().__init__(S, H, instance, verbose, seed, incremental=False)

    def solve(self): 
        if self.sat() == False:
            raise ValueError("Hard clauses are unsatisfiable")
        else:               # Assume that all soft clauses are unary, of the form [x]. 
                            # We will transform the formula to ensure that it occurs EXACTLY ONCE and negated in ONE clause
            softIn = {}     #softIn[x] will be equal to the clause where x occurs
            for c in self.clauses:
                for x in c:
                    if -x in self.weight: #-x is a soft clause
                        if -x in softIn:  #It is the second time it is found
                            newx = self.newVar()
                            newc = [-x,-newx]
                            self.add_clauses([newc])
                            self.weight[newx] = self.weight.pop(-x)
                            softIn.pop(-x)
                            #softIn[newx] = newc  This will we added later as side effect
                        else:
                            softIn[-x] = c                    

            while not self.sat(list(self.weight.keys())):
                core = self.solver.core()
                self.numcores += 1

                if len(core) == 1:                #Cores cannot be empty, but may contain only one soft clause
                    self.cost += self.weight.pop(core[0])                    
                else:
                    w = min([self.weight[i] for i in core], default=math.inf)
                    self.cost += w
                    newVars = []
                    for i in core:
                        if self.weight[i] != w:   #Unfold soft clause in two
                            x = self.newVar()     #New variable for the new soft clause
                            self.weight[x] = self.weight[i] - w
                            self.weight[i] = w
                            c = [-x if  aux == -i else aux for aux in softIn[i]]
                            softIn[x] = c
                            self.add_clauses([c])
                        j = self.newVar()         #New variable for the relaxation of THE clause containing "i"
                        softIn[i].append(j)       #literal j is added to THE clause containing -i
                        newVars.append(j)
                
                    if len(newVars) >= 2:
                        cls, out, lv = sortingNetwork(newVars, self.lastvar)
                        self.add_clauses(cls)
                        self.add_clauses([[-out[-2]]])   # forbid >= 2 trues
                        self.comparators += (lv - self.lastvar) // 2
                        self.lastvar = lv
# len 0/1 => no constraint needed

                if self.verbose:
                    print("Core:", self.numcores, "Size:", len(core), "Comparators:", self.comparators)
                if not self.incremental:
                    self.restart()

            self.model = [x for x in self.solver.model() if abs(x) <= self.originalvar]
            
# Execute this only if file is called directly
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve MaxSAT problems using the Fu&Malik Algorithm.")
    parser.add_argument("input", type=str, help="Input file name")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Verbose")
    parser.add_argument("-s", "--seed", type=int, default=1, help="Random seed (optional)")
    parser.add_argument("-i", "--incremental", action="store_true", default=False, help="Ingremental (default=false) do not create new solver instance at every iteration")
    args = parser.parse_args()

    S, H = readWCNF(args.input)
    mss = FuMalik(S, H, args.input, args.verbose, args.seed, incremental=args.incremental)
    mss.solve()
    mss.printresults()                    
                
                
            
    
