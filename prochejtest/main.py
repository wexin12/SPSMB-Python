# 2 . 5
def prestup(rok):
    return rok % 400 == 0 or ((rok % 4 == 0) and (rok % 100 != 0) )
# 1 . 5
def mean():
    x1 = int(input("Zadej cislo 1: "))
    x2 = int(input("Zadej cislo 2: "))
    x3 = int(input("Zadej cislo 3: "))
    print(f"Prumer je: {(x1 + x2 + x3) / 3}") 
# 3 . 1    
def nums():
    n = int(input("Zadej cislo: "))
    for i in range(n):
        print(f"{i + 1}")
# 3 . 5
def even_sum():
    number = int(input("Zadej cislo: "))
    for i in range(number):
        if i % 2 != 0:


if __name__ == "__main__":
    even_sum()