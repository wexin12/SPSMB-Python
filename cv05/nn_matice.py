import math
from matrix import transform, multiply, apply, plus


def signiod(x):
    return 1 / (1 + math.exp(-x))


def neuron_network(
        X
):
    X = transform(X)
    W = [
        [0.4,0.1, 0.3, 0.4, 0.1, 0.5, -0.2],
        [-0.2, -0.2, 0.1, 0.1, 0.1, 0.1, 0.6],
        [0.4, 0.3, 0.5, 0.5, 0.5, 0.3, 0.0]
    ]
    b =transform([[0.1, 0.6, 0.1]])

    result = multiply(W, X)
    result = plus(result, b)
    return apply(result, signiod)


def do_softmax(items):
    items = items[0]
    total_signoid = sum(items)
    result = []
    for i in items:
        result.append(i/total_signoid)
    return result
    

if __name__ == "__main__":
    X = [
        [0.75, 1, 1, 1, 1, 1, 0] # prznakz/vstup
    ]
    Y = neuron_network( 
        X
        
    )
    Y = transform(Y)
    print(do_softmax(Y))