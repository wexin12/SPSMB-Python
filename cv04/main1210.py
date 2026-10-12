def test_fun():
    i = 6
    j = 7
    return i, j

l = [1, "ahoj", None]     # List
print(l[1])
print(len(l))
for item in l:
    print(item)

if 1 in l:
    pass


l.append(5)              # prida 5 na konec listu
del l[1]                 # smaze prvek na prvnim indexu
l[-1] = 5                # posledni prvek
i, j = test_fun()

tpl = (1, 2, 3,)         # Tuple
print(tpl[1])
print(len(tpl))
for item in tpl:
    print(item)

st = {1,2,3,1,2,3,5,5,4} # Set
print(st)
print(len(st))
for item in st:
    print(item)

dct = {
    "key": "value",
    1    :     5
}
print(dct["key"])