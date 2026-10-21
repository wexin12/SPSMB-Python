import csv


transakce = {}

with open("../../transactions.csv", encoding="utf-8") as file:
    reader = csv.DictReader(file, delimiter=";")
    transakce = {}

    for row in reader:
        fm = row[1]
        to = row[2]
        castka =row[3]
        key = fm + "+" + to

        

