import sqlite3
from datetime import datetime
import hashlib
import os
import getpass
from Export_Data_PDF import export_to_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(BASE_DIR, "expenses.db")

# ---------------- DB SETUP ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT,
            amount REAL,
            type TEXT CHECK(type IN ('Income', 'Expense')),
            note TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ---------------- ADD TRANSACTION ----------------
def add_transaction():
    account = input("Enter account name ( Bank / PB ): ").strip().upper()
    amount = float(input("Amount: "))
    type_ = input("Type (Income/Expense): ").strip().capitalize()
    note = input("Note (optional): ")
    date = input("Date (YYYY-MM-DD) [Leave blank for today]: ").strip()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (account, amount, type, note, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (account, amount, type_, note, date))
    conn.commit()
    conn.close()
    print("✅ Transaction added.\n")

# ---------------- VIEW TRANSACTIONS ----------------
def view_transactions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM transactions ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("No transactions found.\n")
        return

    print(f"{'ID':<3} {'Account':<10} {'Amount':<10} {'Type':<8} {'Date':<12} Note")
    print("-" * 60)
    for r in rows:
        print(f"{r[0]:<3} {r[1]:<10} {r[2]:<10.2f} {r[3]:<8} {r[5]:<12} {r[4]}")
    print()

# ---------------- VIEW BALANCE ----------------
def view_balance():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT account, type, SUM(amount) FROM transactions GROUP BY account, type')
    rows = c.fetchall()
    conn.close()

    balances = {}
    for account, type_, total in rows:
        if account not in balances:
            balances[account] = 0
        if type_ == "Income":
            balances[account] += total
        else:
            balances[account] -= total

    total_balance = sum(balances.values())

    print("\n📊 Account Balances:")
    for acc, bal in balances.items():
        print(f" - {acc}: ₹{bal:.2f}")
    print(f"\n💰 Total Balance: ₹{total_balance:.2f}\n")


PASS_FILE = os.path.join(BASE_DIR, "password.txt")

def set_password():
    password = getpass.getpass("🔐 Set a password for your tracker: ")
    hash_pw = hashlib.sha256(password.encode()).hexdigest()
    with open(PASS_FILE, "w") as f:
        f.write(hash_pw)
    print("✅ Password set. Remember it!\n")

def verify_password():
    if not os.path.exists(PASS_FILE):
        print("No password found. Let's set one!")
        set_password()
        return True
    
    password = getpass.getpass("🔑 Enter your password: ")
    hash_input = hashlib.sha256(password.encode()).hexdigest()

    with open(PASS_FILE, "r") as f:
        stored_hash = f.read().strip()
    
    if hash_input == stored_hash:
        print("✅ Access granted.\n")
        return True
    else:
        print("❌ Incorrect password. Access denied.")
        return False


# ---------------- MENU ----------------
def main():
    if not verify_password():
        return

    init_db()
    while True:
        print("\n📒 Personal Expense Tracker")
        print("1. Add transaction")
        print("2. View all transactions")
        print("3. View balances")
        print("4. Generate PDF report")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            add_transaction()
        elif choice == '2':
            view_transactions()
        elif choice == '3':
            view_balance()
        elif choice == '4':
            export_to_pdf()
        elif choice == '5':
            print("Bye! Stay wealthy, Gudu 💸")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
