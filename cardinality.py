from math import floor, log2

def comparator(i1, i2, o1, o2):
    return [[i1, -o1], [i2, -o1], [-i1,-i2, o1], [-i1, o2], [-i2, o2], [i1, i2, -o2]]


def sortingNetwork(input, lastvar):
    def newVar():
        nonlocal lastvar
        lastvar += 1
        return lastvar

    if len(input) <= 1:
        return [], input, lastvar
    cls = []
    line = { i: input[i] for i in range(len(input)) }
    n = len(input)
    for plog in range(0,floor(log2(n-1))+1):
        p = 2**plog
        for klog in range(plog+1):
            k = p//2**klog
            for j in range(k%p, n-k, 2*k):
                for i in range(0, min(k, n-j-k)):
                    if floor((i+j) / (2*p)) == floor((i+j+k) / (2*p)):
                        i1 = line[i+j]
                        i2 = line[i+j+k]
                        o1 = newVar()
                        o2 = newVar()
                        cls += comparator(i1, i2, o1, o2)
                        line[i+j] = o1
                        line[i+j+k] = o2
    return cls, [ line[i] for i in range(len(input)) ], lastvar
    
def bubbleSort(input, lastvar):
    def newVar():
        nonlocal lastvar
        lastvar += 1
        return lastvar

    if len(input) <= 1:
        return [], input, lastvar
    cls, output, lastvar = bubbleSort(input[:-1], lastvar)
    aux = input[-1]
    newoutput = []
    for o in reversed(output):
        x = newVar()
        y = newVar()
        cls += comparator(o, aux, x, y)
        newoutput = [y] + newoutput
        aux = x
    newoutput = [aux] + newoutput
    return cls, newoutput, lastvar
    
def totalizer(input, lastvar):
    n = len(input)
    if n <= 1:
        return [], input, lastvar
    k1 = n // 2
    k2 = n - k1
    cls1, out1, lastvar = totalizer(input[:k1], lastvar)
    cls2, out2, lastvar = totalizer(input[k1:], lastvar)
    output = [lastvar + i for i in range(1, n+1)]
    lastvar += n
    cls = []
    for i in range(k1):
        for j in range(k2):
            cls.append([-out1[i], -out2[j], output[i+j]])
            cls.append([out1[i], out2[j], -output[i+j+1]])
    for i in range(k1):
        cls.append([out1[i], -output[i]])
        cls.append([-out1[k1-1-i], output[n-1-i]])
    for j in range(k2):
        cls.append([out2[j], -output[j]])
        cls.append([-out2[k2-1-j], output[n-1-j]])
    return cls1 + cls2 + cls, output, lastvar
            
