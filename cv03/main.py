

if __name__ == "__main__":
    str_time = input("Zadej cas v S: ")
    time = int(str_time)
    hour = time // 3600
    time = time - 3600 * hour
    minut = time // 60
    time = time - 60 * minut
    sekund = time
    print(f"{hour}:{minut}:{sekund}")


