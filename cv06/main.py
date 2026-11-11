import math

def signiod(x):
    return 1 / (1 + math.exp(-x))


def neuron_network(
        is_one,
        is_two,
        is_three,
        is_four,
        is_five,
        is_six,
        is_seven,
        is_eight,
        is_nine,
        is_zero
):
    pass


def do_softmax(items):
    total_signoid = sum(items)
    for index, i in enumerate(items):
        print(f"{index} -> {i / total_signoid}")