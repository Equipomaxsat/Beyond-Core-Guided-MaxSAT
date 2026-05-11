import random
import itertools as itr
import argparse
from tools import printWCNF, printXOR


def generadorPHP(m, n, s=0):  #Asumimos que m > n. Asigna las variables empezando por la paloma 1 hasta la m. Por ejemplo, si PHP(3,2), entonces empieza p11->1 p12->2 p21->3 p22->4....)
    
    if s is not None:
        random.seed(s)
    var = list(range(1, m*n + 1))
        
    total = [ var[i*n : (i+1)*n] for i in range(m) ]
    inj = [ list(pair) for j in range(n)
                       for pair in itr.combinations([-var[i*n + j] for i in range(m)], 2) ]       
    return total, inj


def randomF(n, m, k=3, s=0): #Generador de random k-formulas con n variables y m clausulas

    if s is not None:
        random.seed(s)
    return [ [x if random.random() < 0.5 else -x for x in random.sample(range(1, n+1), k)] for i in range(m) ]
        

def smallworld(n, m, k=2, s=0):
    if s is not None:
        random.seed(s)
    return [ [x % n + 1 if random.random() < 0.5 else -(x % n + 1) for x in [ s+i for s in [random.randrange(n)] for i in range(k) ] ] for j in range(m) ]

def randomXOR(n, m, k=2, s=0):

    if s is not None:
        random.seed(s)
    return [ (1, random.sample(range(1, n+1), k), 1 if random.random() < 0.5 else -1) for j in range(m) ]    


def randomCUT(n, m, k=2, s=0):

    if s is not None:
        random.seed(s)
    return [ (1, random.sample(range(1, n+1), k), -1) for j in range(m) ]    


# Execute this only if file is called directly to generate model directly on standard output
if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description="Generator of SAT formulas following some standard models.")
    parser.add_argument("model", type=str, help="Models are: rnd, php, xor, cut, sw")
    parser.add_argument("-n", type=int, help="Number of variables/holes")
    parser.add_argument("-m", type=int, help="Number of clauses/pigeons")
    parser.add_argument("-k", type=int, default=2, help="Size of clauses")
    parser.add_argument("-o", "--output", type=str, help="Output file name (optional)")
    parser.add_argument("-s", type=int, help="Random seed (optional)")
    args = parser.parse_args()

    if args.model == "rnd":
        printWCNF(args.output, randomF(args.n, args.m, args.k, args.s))
    elif args.model == "php":
    	S,H = generadorPHP(args.m, args.n, args.s)
    	printWCNF(args.output, S, H)
    elif args.model == "xor":
        printXOR(args.output, randomXOR(args.n, args.m, args.k, args.s))
    elif args.model == "cut":
        printXOR(args.output, randomCUT(args.n, args.m, args.k, args.s))
    elif args.model == "sw":
        printWCNF(args.output, smallworld(args.n, args.m, args.k, args.s))
    else:
    	print("ERROR: Wrong model name")
    	    
    	    

