def zeros(m, n):
    matrix_c = []
    for i in range(m):
        matrix_c.append([])
        for j in range(n):
            matrix_c[i].append(0)
    return matrix_c


def plus(matrix_a, matrix_b):
    matrix_c = []
    for i in range(len(matrix_a)):
        matrix_c.append([])
        for j in range(len(matrix_a[0])):
           matrix_c[i].append(matrix_a[i][j] + matrix_b[i][j])
    return matrix_c       

def minus(matrix_a, matrix_b):
    matrix_c = []
    for i in range(len(matrix_a)):
        matrix_c.append([])
        for j in range(len(matrix_a[0])):
           matrix_c[i].append(matrix_a[i][j] - matrix_b[i][j])
    return matrix_c 
    
    
def eyes(m, n):
    matrix_c = []
    for i in range(m):
        matrix_c.append([])
        for j in range(n):
            if i == j:
                matrix_c[i].append(1)
            else:
                matrix_c[i].append(0)
    return matrix_c

def size_of(matrix):
    return (len(matrix), len(matrix[0]))

def format(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            print(f"{matrix[i][j]}", end=" ")
        print(" ")  

def transform(matrix):
    m, n =size_of(matrix)
    result = zeros(n, m)
    for i in range(m):
        for j in range(n):
            result[j][i] = matrix[i][j]
    return result    

def apply(matrix, func):
    m, n = size_of(matrix)
    result = zeros(m, n)
    for i in range(m):
        for j in range(n):
            result[i][j] = func(matrix[i][j])
    return result        

        
def multiply_constant(matrix, const):
    m, n = size_of(matrix)
    result = zeros(m, n)
    for i in range(m):
        for j in range(n):
            result[i][j] = matrix[i][j] * const
    return result   


def multiply(matrix_a, matrix_b):
    mA, nA = size_of(matrix_a)
    mB, nB = size_of(matrix_b)
    if nA != nB:
        print("Nejde to!")
    result = zeros(mA, nB)
    for i in range(mA):
        for j in range(nB):
            suma = 0
            for l in range(nA):
                suma += matrix_a[i][l] * matrix_b[l][j]
            result[i][j] = suma
    return result         
