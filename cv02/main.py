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
    user_bilance = 1_000
    print("Vytej bohaty jedince")
    while True:
      i = input(f"Zadej sve bohatsvi: ({user_bilance} eur):")
      if not i.isnumeric():
        continue
      bet = int(i)
      print("Select color:")
      print("\t\t0 - Cervena")   # 48.5%
      print("\t\t1 - Cerna") # 48.5%
      print("\t\t2 - Zeleba") # 3%
      print("\t\t9 - Zelenac")
      s = input("Vyber: ")
      if not s.isnumeric():
        continue
      selection = int(s)
      if selection == 9:
        return
      elif selection not in [0, 1, 2]:
        print("Ty si fakt pokemon")
        continue
      if selection == get_color():
          user_bilance = user_bilance + bet * 2
          print("Vyhral")
      else:
          print("Prohral")
          user_bilance = user_bilance - bet
 
 
if __name__ == "__main__":
    start_game()