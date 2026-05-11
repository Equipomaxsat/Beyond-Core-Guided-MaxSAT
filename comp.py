# Version 1
# bestcombinable are the BFs that minimize number of ones in their AND


import sys
import argparse
import random, math
from optilog.solvers.sat import Glucose41
from bitarray import bitarray
from bitarray.util import count_xor, count_and, count_or
from maxSATsolver import MaxSATsolver
from tools import readWCNF

# Assume that the MaxSAT problem is composed by a set of hard clauses F, and a set of unary solft clauses with weights L
# Each soft clause X describes a Boolean function "BF" that returns the value True for all models of F U {X}

#TODO: Add solver as element of MaxSATsolver

class Comparator(MaxSATsolver):
    def __init__(self, S, H=None, instance="stdin", verbose=False, seed=1, initmodels=1, heuristic=1, coreguided=False, incremental=False):
        super().__init__(S, H, instance, verbose, seed, incremental)
        self.candidates = []
        self.assigns = { x : bitarray() for x,_ in self.weight.items() }    # One bitarray for each BF
        self.focus = None
        self.removals = 0
        self.assignments = 0
        self.comparators = 0
        self.bestcomb = set()   # For every pair the number of ones in their XOR
        self.initmodels = initmodels
        self.heuristic = heuristic
        self.coreguided = coreguided

    def dump(self):
        super().dump()
        print("Candidates = ", self.candidates)
        print("Assigns = ", self.assigns)
        print("Weights = ", self.weight)
        print("Last var = ", self.lastvar)
        print("Upper-bound cost = ", self.ubcost)
        print("Best Combinations = ", self.bestcomb)
        print("--------------------")
            
    def initialize(self):
        # Evaluates BFs on several models of hard clauses
        # Set ubcost = minimal, for all models, of number BF evaluated to False
        # Set candidates = list of BF evaluated to false for all assignments
        
        if not self.sat():
            raise ValueError("Hard clauses are unsatisfiable or too much initial models")
        
        soft = [i for i in self.assigns]
        
        for i in range(self.initmodels):     
            random.shuffle(soft)
            for i in range(len(soft)):            # Try to satisfy as many soft clauses as possible
                if self.sat(soft[:(i+1)]): 
                    self.addassignment(set(self.solver.model()))
                else:
                    self.focus = set(self.solver.core())
                    break
            if self.ubcost == 0:
                break                
        self.candidates = [x for x,A in self.assigns.items() if A.count(1) == 0]
        
        
    def addassignment(self, model):
        # Adds model to the set of assignments,
        # Sets upper-bound of cost accordingly
        # Removes from candidates BFs evaluated to True by the model
        # Actualize bestcomb adding one when coordinates of bitarrays are both ones

        cost = 0
        for x in self.assigns:
            if x in model:
                self.assigns[x].append(1)
                if x in self.candidates:
                    self.candidates.remove(x)
            else:    # -x in model
                self.assigns[x].append(0)
                cost += self.weight[x]
        self.ubcost = min(self.ubcost, cost)
        if cost == self.ubcost:
            self.model = [i for i in model if abs(i) <= self.originalvar]


    def bestcombinable1(self, soft):
        soft = soft & self.assigns.keys()

        k1 = {i: self.assigns[i].count(1) for i in soft}
        m1 = min(k1.values())
        B1 = [i for i, v in k1.items() if v == m1]

        k2 = {(i, j): count_and(self.assigns[i], self.assigns[j])
              for i in B1 for j in soft if i != j}
        m2 = min(k2.values())
        B2 = [p for p, v in k2.items() if v == m2]

        k3 = {p: count_or(self.assigns[p[0]], self.assigns[p[1]]) for p in B2}
        m3 = min(k3.values())
        B3 = [p for p, v in k3.items() if v == m3]

        k4 = {p: min(self.weight[p[0]], self.weight[p[1]]) for p in B3}
        m4 = max(k4.values())
        B4 = [p for p, v in k4.items() if v == m4]

        return random.choice(B4)

                            
    def bestcombinable2(self, soft):
        soft = soft & self.assigns.keys()

        k1 = {
            (i, j): min(
                (self.assigns[i] & (~self.assigns[j])).count(1),
                (self.assigns[j] & (~self.assigns[i])).count(1),
            )
            for i in soft for j in soft if i < j
        }
        m1 = max(k1.values())
        B1 = [p for p, v in k1.items() if v == m1]   # list of pairs (i,j)

        k2 = {p: min(self.weight[p[0]], self.weight[p[1]]) for p in B1}
        m2 = max(k2.values())
        B2 = [p for p, v in k2.items() if v == m2]

        return random.choice(B2)


    def combine(self, i, j):
        # Creates a pair of new BF: x = AND(i,j) y = OR(i,j)
        # Removes the old i,j or actualize their weights
        # Compute best compinations for the new BFs
        
        x = self.newVar()
        y = self.newVar()
        self.bestcomb.add((x,y))
        if self.weight[i] < self.weight[j]:
            i,j = j,i

    
        self.assigns[x] = self.assigns[i] & self.assigns[j]
        self.assigns[y] = self.assigns[i] | self.assigns[j]
        self.weight[x] = self.weight[j]
        self.weight[y] = self.weight[j]
        self.assigns.pop(j)
        if self.weight[i] == self.weight[j]:
            self.assigns.pop(i)
        else:
            self.weight[i] -= self.weight[j]
        
        self.candidates = [x for x,A in self.assigns.items() if A.count(1) == 0]
        cls = [[i, -x], [j, -x], [-i,-j, x], [-i, y], [-j, y], [i,j, -y]]
        self.clauses += cls
        return x, y, cls
        

    def solve(self):
        self.initialize()
        while self.ubcost > 0:

            if len(self.focus) == 1 or len(self.candidates) > 0:
                if len(self.focus) == 1:
                    c = next(iter(self.focus))
                else:
                    c = self.candidates[0]
                
                # There is a candidate c to be unsatisfiable 
                
                if not self.incremental:
                    self.restart()
                if (not (len(self.focus) == 1 and self.coreguided)) and self.sat([c]):
                    # c was satisfiable, add a new model
                    
                    self.addassignment(self.solver.model())
                    self.assignments += 1
                    if self.verbose:
                        print("ADDING ASSIGNMENT FOR", c,": cost", self.cost, "upper bound", self.ubcost, "candidates:", self.candidates)
                else:
                    # c was really an unsatisfiable soft formula

                    self.numcores += 1
                    self.candidates.remove(c)
                    self.assigns.pop(c)
                    self.ubcost -= self.weight[c]
                    self.cost += self.weight[c]
                    self.removals += 1
                    if self.verbose:
                        print("REMOVE ", c, ": cost", self.cost, "upper bound", self.ubcost, "focus", self.focus, "\n")

                    if self.coreguided:
                        if self.sat([x for x in self.assigns]):
                            self.addassignment(self.solver.model())
                            self.assignments += 1
                            if self.verbose:
                                print("ALL SOFT CLAUSES SATISFIED")
                        else:
                            self.focus = set(self.solver.core())
                            if self.verbose:
                                print("NEW CORE ", len(self.focus), "core:", self.focus, "\n")
                    else:
                        self.focus = set(self.assigns.keys())
                        if self.verbose:
                            print("NEW FOCUS ", len(self.focus), "focus:", self.focus, "\n")

            else:
                # There are not candidates to be unsatisfiable, combine two soft formulas
                
                if self.heuristic == 1:
                    i,j = self.bestcombinable1(self.focus)
                else:
                    i,j = self.bestcombinable2(self.focus)
                x,y,cls = self.combine(i,j)
                self.focus.add(x)
                # self.focus.add(y)
                self.focus.remove(i)
                self.focus.remove(j)
                self.add_clauses(cls)
                self.comparators += 1
                if self.verbose:
                    print("COMBINE",i,j, "->",x,y, "cost:", self.cost, "upper bound:", self.ubcost)

 
# Execute this only if file is called directly
if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description="Solve MaxSAT problems using the Fu&Malik Algorithm.")
    parser.add_argument("input", type=str, help="Input file name")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Verbose")
    parser.add_argument("-s", "--seed", type=int, default=1, help="Random seed (optional)")
    parser.add_argument("-m", "--initmodels", type=int, default=1, help="Number of initial models (default=1)")
    parser.add_argument("-H", "--heuristic", type=int, default=1, help="Heuristic (1 or 2)")
    parser.add_argument("-i", "--incremental", action="store_true", default=False, help="Incremental (default=false) do not create new solver instance at every iteration")
    parser.add_argument("-c", "--coreguided", action="store_true", default=False, help="Only combine pairs of soft clauses from a core (default=false)")
    args = parser.parse_args()

    S, H = readWCNF(args.input)
    mss = Comparator(S, H, args.input, args.verbose, args.seed, args.initmodels, args.heuristic, args.coreguided, incremental=args.incremental)
    mss.solve()
    mss.printresults()
