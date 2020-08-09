import random
import sqlite3


def check_checksum(card_number):
    n_str = card_number[:15]
    checksum = card_number[15:16]
    total = 0
    for i in range(len(n_str)):
        x = int(n_str[i])
        if (i + 1) % 2 == 0:
            total += x
        else:
            x2 = x * 2
            if x2 > 9:
                x2 -= 9
            total += x2
    return (10 - (total % 10)) % 10 == int(checksum)


class Card:

    def __init__(self):
        self.bin = "400000"
        self.account_number = str(random.randint(0, 1000000000)).zfill(9)
        self.checksum = str(self.calc_checksum())
        self.card_number = self.bin + self.account_number + self.checksum
        self.pin = str(random.randint(0, 10000)).zfill(4)

    def calc_checksum(self):
        n_str = self.bin + self.account_number
        total = 0
        for i in range(len(n_str)):
            x = int(n_str[i])
            if (i + 1) % 2 == 0:
                total += x
            else:
                x2 = x * 2
                if x2 > 9:
                    x2 -= 9
                total += x2
        return (10 - (total % 10)) % 10

    def __str___(self):
        return self.card_number


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
try:
    cur.execute('''
        CREATE TABLE card(
            id INTEGER PRIMARY KEY,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0
        )
        ''')
except sqlite3.OperationalError:
    pass

while True:
    print()
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

    menu_input = input()
    print()

    if menu_input == "0":
        print("Bye")
        cur.close()
        conn.close()
        exit(0)

    elif menu_input == "1":
        card = Card()
        cur.execute('INSERT INTO card (number, pin) VALUES (?, ?)',
                    (card.card_number, card.pin))
        conn.commit()
        print("Your card has been created")
        print("Your card number:")
        print(card.card_number)
        print("Your card PIN:")
        print(card.pin)

    elif menu_input == "2":
        print("Enter your card number:")
        card_num = input()
        print("Enter you PIN:")
        pin = input()
        print()
        cur.execute('''SELECT balance FROM card 
                              WHERE number = ? AND pin = ?''',
                    (card_num, pin))
        row = cur.fetchone()
        if row is not None:
            print("You have successfully logged in!")
            while True:
                cur.execute('''SELECT balance FROM card 
                        WHERE number = ?''',
                        [card_num])
                row = cur.fetchone()
                balance = row[0]
                print()
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")
                logged_in_menu_input = input()
                print()
                if logged_in_menu_input == "0":
                    print("Bye")
                    cur.close()
                    conn.close()
                    exit(0)
                elif logged_in_menu_input == "1":
                    print("Balance: {}".format(balance))
                elif logged_in_menu_input == "2":
                    print("Enter income:")
                    income = int(input())
                    new_balance = balance + income
                    cur.execute('''UPDATE card SET balance = ?
                                WHERE number = ?''',
                                (new_balance, card_num))
                    conn.commit()
                    print("Income was added!")
                elif logged_in_menu_input == "3":
                    print("Transfer")
                    print("Enter card number:")
                    transfer_card_num = input()
                    cur.execute('''SELECT balance FROM card 
                                WHERE number = ?''',
                                [transfer_card_num])
                    transfer_row = cur.fetchone()
                    if transfer_card_num == card_num:
                        print("You can't transfer money to the same account!")
                    elif not check_checksum(transfer_card_num):
                        print("Probably you made mistake in the card number. Please try again!")
                    elif transfer_row is None:
                        print("Such a card does not exist.")
                    else:
                        print("Enter how much money you want to transfer:")
                        transfer_amount = int(input())
                        if transfer_amount > balance:
                            print("Not enough money!")
                        else:
                            transfer_balance = transfer_row[0]
                            new_transfer_balance = transfer_balance + transfer_amount
                            new_balance = balance - transfer_amount
                            cur.execute('''UPDATE card SET balance = ?
                                        WHERE number = ?''',
                                        (new_transfer_balance, transfer_card_num))
                            cur.execute('''UPDATE card SET balance = ?
                                        WHERE number = ?''',
                                        (new_balance, card_num))
                            conn.commit()
                elif logged_in_menu_input == "4":
                    cur.execute('''DELETE FROM card 
                                WHERE number = ?''',
                                [card_num])
                    conn.commit()
                    print("The account has been closed!")
                    break
                elif logged_in_menu_input == "5":
                    print("You have successfully logged out!")
                    break
        else:
            print("Wrong card number or PIN!")
