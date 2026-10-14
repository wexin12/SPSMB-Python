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
    soucet = 0
    for i in range(number):
        if i % 2 != 0:
            soucet = soucet + i
    return soucet   
# 3 . 2
def backwards():
    number = int(input("Zadej cislo: "))
    for i in range(number):
        print(f"{number - i}") 
# 3 . 6 
def nasobilka():
    number = int(input("Zadej cislo: "))
    for i in range(10):
        print(f"{number * (i + 1)}")
#7 . 1
def min():
    number = int(input("Zadej cislo:"))
    min = number
    while number != -1:
        if min > number:
            min = number
        number = int(input("Zadej cislo: "))
    print(f"min je: {min}")          
# 3 . 3
def soucet():
    number = int(input("Zadej cislo"))
    sum = (number * (number + 1) / 2)
    print(f"{sum}")
# 3 . 4
def odd_sum():
    number = int(input("Zadej cislo: "))
    soucet = 0
    for i in range(number):
        if i % 2 == 0:
            soucet = soucet + i
    return soucet    
# 4 . 1
def faktorial_ez():
    faktorial = 1
    number = int(input("Zadej cislo: "))
    for i in range(number):
        faktorial = faktorial * (i + 1)
    return faktorial   
# 5 . 1
def combination_num():
    number = int(input("Zadej cislo: "))
    k = int(input("Zadej cislo: "))
    print(faktorial_ez(number) / ( faktorial_ez(k) * ( faktorial_ez(number - k))))
# 4 . 2
def factorial_rekurze(number):
    if number <= 0:
        return 1
    return factorial_rekurze((number - 1)) * number 
# 2 . 1
def odd_or_even():
    number = int(input("Zadej cele cislo: "))
    if number % 2 == 0:
        return True
    return False
#  15 . 1
def area_():
    a = int(input("Zadej stranu a: "))
    b = int(input("Zadej stranu b: "))
    print(f"Obsah je: {a * b}")
    print(f"Obvod je: { 2 * a + 2 * b}")
# 15 . 2
def circle():
    r = int(input("Zadej poloměr: "))
    print(f"Obvod kruhu je: { 2 * 3.14 * r}")
    print(f"Obsah kruhu je: {3.14 * (r ** 2)}")
# 2 . 4
def biggest():
    a1 = int(input("Zadej cislo: "))
    a2 = int(input("Zadej cislo "))
    a3 = int(input("Zadej cislo: "))
    highest = max (a1, a2, a3)
    print(highest)
# 15 . 3
def pythagoras():
    number = int(input("Zadej odvesnu: "))
    number2 = int(input("Zadej odvesnu 2:"))
    c =((number ** 2) + (number2 ** 2)) ** 0.5
    print(c)
# 7 . 3
def prumer():
    N = int(input("Zadej pocet prvku: "))
    numbers = []
    for i in range(N):
        number = int(input(f"Zadej {i + 1} cislo: "))
        numbers.append(number)
    print(sum(numbers) / len(numbers))    
# 7 . 5
def zjistipocetcifer():
    N = int(input("Zadej cislo: "))
    list = []
    while N != 0:
        list.append(N % 10)
        N = N // 10
    print(len(list))   # 7 .6 print(sum(list)) 7.7 print(list)
#9.1
def NSD():
    a = int(input("Zadej cislo a: "))
    b = int(input("Zadej cislo b: "))
    r = 1
    while r != 0:
        r = (a % b)
        a = b
        b = r
    print(f"Nejmensi spolecny delitel je {a}")
# 11. 1
def findout():
    text = input("Zadej text: ")
    print(len(text))
# 11 . 3
def palindrom():
    text = input("Zadej text: ")
    pal = text[::-1]
    if pal == text:
        print("Zadane slovo je palindrom")
    else:
        print("Zadane slovo neni palidrom1")
# 11 . 4
def samo():
    pocet = 0
    text = input("Zadej text: ")
    list = ["a", "e", "i", "o", "u", "y"]
    for i in range(len(text)):
        for j in range(len(list)):
            if text[i] == list[j]:
                pocet = pocet + 1
    return pocet            
def znaky():
    counter = 0
    text = input("Zadek text: ")
    dct = {}
    for i in text:
        if i in dct.keys():
            counter = dct[i]
        else:
            dct[i] = 1
    print(dct) 
# 12 . 1
def soucet_list():
    N = input("Zadej cisla: ")
    number =[] 
    for i in N.split():
        number.append(int(i))
    print(sum(number))
# 12 . 3
def seznam():
    N = input("Zadej cisla: ")
    number = []
    for i in N.split():
        number.append(int(i))
    print(number[::-1])                        
# 12.4
def dupe():
    N = input("Zadejte cisla: ")
    cislo = []
    for i in N.split():
        a = int(i)
        if a not in cislo:
            cislo.append(a)
    print(cislo)        
# 12 . 2
def maxmin():
    N = input("Zadejte cisla: ")
    numbers = []
    min = float("inf")
    max = float("-inf")
    for i in N.split():
        a = int(i)
        if a > max:
            max = a
        if a < min:
            min = a    
    print(f"max {max} min {min}")        

if __name__ == "__main__":
    maxmin()