import sys
import argparse
import math
from maxSATsolver import MaxSATsolver
from tools import readWCNF


def conjunctionNetwork(C, lv):
    if len(C) == 1:
        return [], C, lv
    else:
        n = len(C) // 2
        cls1, o1, lv1 = conjunctionNetwork(C[:n], lv)
        cls2, o2, lv2 = conjunctionNetwork(C[n:], lv1)
        x = o1[0]
        y = o2[0]
        x_and_y = lv2+1
        x_or_y = lv2+2
        cls = cls1 + cls2 + [[-x_and_y, x], [-x_and_y, y], [-x, -y, x_and_y], [x_or_y, -x], [x_or_y, -y], [x, y, -x_or_y]]
        o = [x_and_y] + o1[1:] + [x_or_y] + o2[1:]
        return cls, o, lv2+2

class OLL(MaxSATsolver):

    def __init__(self, S, H=None, instance="stdin", verbose=False, seed=1, incremental=False):
        super().__init__(S, H, instance, verbose, seed, incremental)
        
    def solve(self): 
        if self.sat() == False:
            raise ValueError("Hard clauses are unsatisfiable")
        else:
            while not self.sat(list(self.weight.keys())):
                core = self.solver.core()
                self.numcores += 1
                if len(core) == 1:                #Cores cannot be empty, but may contain only one soft clause
                    self.cost += self.weight.pop(core[0])
                else:
                    w = min([self.weight[i] for i in core], default=math.inf)
                    self.cost += w
                    for i in core:
                        if self.weight[i] != w:   #Unfold soft clause in two
                            self.weight[i] -= w
                        else:
                            self.weight.pop(i)
                
                    cls, output, lv = conjunctionNetwork(core, self.lastvar)
                    self.comparators += (lv - self.lastvar) // 2
                    self.lastvar = lv
                    self.add_clauses(cls)
                    for x in output[1:]:        #First output is unsatisfiable
                        self.weight[x] = w

                if self.verbose:
                    print("Core:", self.numcores, "Size:", len(core), "Comparators:", self.comparators)
                
                if not self.incremental:
                    self.restart()

            self.model = [x for x in self.solver.model() if abs(x) <= self.originalvar]
            
# Execute this only if file is called directly
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve MaxSAT problems using the OLL Algorithm.")
    parser.add_argument("input", type=str, help="Input file name")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Verbose")
    parser.add_argument("-s", "--seed", type=int, default=1, help="Random seed (optional)")
    parser.add_argument("-i", "--incremental", action="store_true", default=False, help="Ingremental (default=false) do not create new solver instance at every iteration")
    args = parser.parse_args()

    S, H = readWCNF(args.input)
    mss = OLL(S, H, args.input, verbose=args.verbose, seed=args.seed, incremental=args.incremental)
    mss.solve()
    mss.printresults()
                    
                
                
            
    
