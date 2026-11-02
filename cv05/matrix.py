def plus(matrix_a, matrix_b):
    matrix_c = []
    for i in range(len(matrix_a)):
        matrix_c.append([])
        for j in range(len(matrix_a[0])):
           matrix_c[i].append(matrix_a[i][j] + matrix_b[i][j])
    return matrix_c       

def minus(matrix_a, matrix_b): 
    

