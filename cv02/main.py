from random import random

def get_color():
    value = random() * 100
    if value <= 3:
        return 2
    elif value <= 51.5:
        return 0
    else:
        return 1

def start_game():
    user_bilance = 1000
    print("Vitej bohaty jedince")

    bet = int (input(f"Vyber si sázku ({user_bilance}eur): "))
    print("Vyber si barvu stesti")
    print("\t\t0- Cervena") # 48.5%
    print("\t\t1- Cerna")   # 48.5%
    print("\t\t2- Zelena")  # 3%
    print("\t\t9- Opustit ? :(")
    selection = int (input("Vybrana: "))


    if selection == 9:
        return

    if selection == get_color():
        user_bilance = user_bilance + bet * 2
        print("Vyhral")
    else:
        print(f"Prohral {bet} eur") 
        user_bilance = user_bilance - bet   



if __name__ == "__main__":
    start_game()
         