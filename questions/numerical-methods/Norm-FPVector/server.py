import random
import numpy as np
import numpy.linalg as la
import prairielearn as pl

def generate(data):

    # number of bits in significand, after leading 1
    n = random.choice([2, 3])

    # number of dimensions in x
    d = random.choice([2, 3])

    # the p-norm to use
    p = random.choice([1, 2, np.inf])

    i = random.choice([0, 1, 2])
    exps = [(-15, 16), (-31, 32), (-63, 64), ][i]
    exp_lower, exp_upper = exps


    # convert from a float using all bits
    def to_number(x, e):
        s = 0
        for i in range(len(x)):
            s += x[i]*2**(e-i)
        return s


    # convert from a float with n bits in the siginificand
    def to_float(x, e):
        s = 0
        # use the leading 1 and the next rand digits.
        for i in range(n+1):
            s += x[i]*2**(e-i)
        return s
    
    x = []
    es = []
    for _ in range(d):
        # the leading digit is the left most number in the list
        s = [1]
        # the true answer has up to 2 more bits.
        for i in range(n+2):
            s.append(random.choice([0, 1]))
        x.append(s)
        es.append(random.choice([0,1,2]))

    # transform these lists of binary strings 
    # into vectors of decimal numbers
    xt = []
    xf = []
    for i in range(d):
        xt.append(to_number(x[i], es[i]))
        xf.append(to_float(x[i], es[i]))
    xt = np.array(xt).reshape((d, 1))
    xf = np.array(xf).reshape((d, 1))


    s = ""
    for i in range(1, n+1):
        s += "s_" + str(i)
    representation = "$(1." + s + ")_2\\times 2^{m}$"
    exp_range = f"$m \\in [{exp_lower}, {exp_upper}]$"


    data['params']['representation'] = representation
    data['params']['exp_range'] = exp_range

    data['params']['x'] = pl.to_json(xt)

    data['params']['d'] = d
    data['params']['p'] = f"${p}$" if p != np.inf else "$\\infty$"

    # have to check that these norms are >1
    data['params']['incorrect1'] = la.norm(xf, p)*2**-n
    data['params']['incorrect2'] = 2**-(n-d)
    data['params']['incorrect3'] = d*2**-n

    # machine epsilon is the answer, for any p-norm and any dimension.
    data['params']['correct'] = 2**-n

    data['correct_answers']['rel-err'] = la.norm(xt - xf, p)/la.norm(xt, p)


    return data