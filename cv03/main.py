def nacas():
    str_time = input("Zadej cas v S: ")
    time = int(str_time)
    hour = time // 3600
    time = time - 3600 * hour
    minut = time // 60
    time = time - 60 * minut
    sekund = time
    print(f"{hour}:{minut}:{sekund}")

if __name__ == "__main__":
    value = int(input("Zadej castku "))  
    array = [5000,2000,1000,500,200,100,50,20,10,5,2,1]
    for item in array:
        pocet = value // item
        value = value - (item * pocet)
        print(f"{pocet}: {item}")



