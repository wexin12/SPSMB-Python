import csv

transakce = []
pocet = 0

with open("../transactions.csv", encoding="utf-8") as file:
    reader = csv.DictReader(file, delimiter=";")

    for row in reader:
        od = row["from"]
        komu = row["to"]
        castka = float(row["value"])

        transakce.append((od, komu, castka))

for i in range(len(transakce)):
    od1, komu1, castka1 = transakce[i]

    for j in range(i + 1, len(transakce)):
        od2, komu2, castka2 = transakce[j]

        if od1 == komu2 and komu1 == od2 and castka1 == castka2:
            pocet += 1
            print(f"{od1} a {komu1}: {castka1} pocet transakcich: {pocet}")



        