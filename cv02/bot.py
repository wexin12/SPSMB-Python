import subprocess
import random
import time
import sys


GAME_FILE = "main.py"


def choose_bet(balance):
    """
    Bot zvolí sázku.
    Stejná logika jako v původním botovi.
    """

    if balance < 10:
        return None

    max_bet = max(10, int(balance * 0.10))
    max_bet = min(max_bet, balance)

    return random.randint(10, max_bet)


def choose_color():
    """
    Výběr barvy bota.

    0 = červená
    1 = černá
    2 = zelená
    """

    choices = [
        0, 0, 0,
        1, 1, 1,
        2
    ]

    return random.choice(choices)


def run_bot():

    print("🤖 Bot se připojuje ke hře...")
    time.sleep(1)

    # -u = Python poběží bez bufferování výstupu.
    #
    # Díky tomu bot okamžitě uvidí printy
    # z původní hry.
    process = subprocess.Popen(
        [
            sys.executable,
            "-u",
            GAME_FILE
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=0
    )

    balance = 1000
    current_bet = None

    # Text, který už bot přečetl.
    buffer = ""

    try:

        while True:

            # ČTEME JEDEN ZNAK.
            #
            # Toto je důležité, protože původní hra má:
            #
            # input("Zadej sve bohatsvi...")
            #
            # a prompt nemá newline.
            char = process.stdout.read(1)

            if char == "":
                break

            # Ukážeme výstup původní hry
            # normálně v terminálu.
            print(char, end="", flush=True)

            buffer += char

            # Aby buffer nerostl donekonečna,
            # necháme si pouze posledních 500 znaků.
            if len(buffer) > 500:
                buffer = buffer[-500:]

            # ==================================================
            # HRA CHCE SÁZKU
            # ==================================================

            if "Zadej sve bohatsvi:" in buffer:

                # Malá pauza, aby to vypadalo
                # jako normální uživatel.
                time.sleep(random.uniform(0.5, 1.5))

                current_bet = choose_bet(balance)

                if current_bet is None:
                    print("\n🤖 Bot nemá dostatek peněz.")
                    break

                print(
                    f"\n🤖 BOT → sázka: "
                    f"{current_bet} EUR"
                )

                process.stdin.write(
                    str(current_bet) + "\n"
                )

                process.stdin.flush()

                # Důležité:
                # odstraníme nalezený prompt z bufferu,
                # aby se nezpracoval znovu.
                buffer = ""

                continue

            # ==================================================
            # HRA CHCE VÝBĚR BARVY
            # ==================================================

            if "Vyber:" in buffer:

                time.sleep(random.uniform(0.5, 1.2))

                selection = choose_color()

                color_names = {
                    0: "🔴 Červená",
                    1: "⚫ Černá",
                    2: "🟢 Zelená"
                }

                print(
                    f"\n🤖 BOT → "
                    f"{color_names[selection]}"
                )

                process.stdin.write(
                    str(selection) + "\n"
                )

                process.stdin.flush()

                buffer = ""

                continue

            # ==================================================
            # VÝHRA
            # ==================================================

            if "Vyhral" in buffer:

                if current_bet is not None:

                    balance += current_bet * 2

                    print(
                        f"\n🤖 BOT → "
                        f"bilance: {balance} EUR"
                    )

                buffer = ""

                continue

            # ==================================================
            # PROHRA
            # ==================================================

            if "Prohral" in buffer:

                if current_bet is not None:

                    balance -= current_bet

                    print(
                        f"\n🤖 BOT → "
                        f"bilance: {balance} EUR"
                    )

                buffer = ""

                continue

    except KeyboardInterrupt:

        print("\n\n🛑 Bot ručně ukončen.")

    finally:

        try:
            process.terminate()
            process.wait(timeout=2)

        except Exception:

            try:
                process.kill()
            except Exception:
                pass

        print("\n🤖 Bot skončil.")


if __name__ == "__main__":
    run_bot()
