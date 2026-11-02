from matrix import plus

if __name__ == "__main__":
    matrix_a = [
        [1, 0, 1],
        [0, 1, 0],
        [0, 0, 1]
    ]
    matrix_b = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

matrix_c = plus(matrix_a, matrix_b)
print(matrix_c)