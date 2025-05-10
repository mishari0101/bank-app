# ------------------------- Imports -------------------------
import json
import hashlib
import os

# ------------------------- Constants & Data -------------------------
DATA_FILE = "bank_data.json"
bank_accounts = {}
next_account_number = 10001

# ------------------------- Utility Functions -------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_data():
    global bank_accounts, next_account_number
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            bank_accounts = data.get("accounts", {})
            next_account_number = data.get("next_account_number", 10001)

def save_data():
    data = {
        "accounts": bank_accounts,
        "next_account_number": next_account_number
    }
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
    print("Data saved successfully.")

def generate_account_number():
    global next_account_number
    account_no = next_account_number
    next_account_number += 1
    return str(account_no)

def authenticate(account_no, password):
    account = bank_accounts.get(account_no)
    if not account:
        return False
    return account["password"] == hash_password(password)

# ------------------------- Core Banking Functions -------------------------
def create_account():
    name = input("Enter your name: ").strip()
    password = input("Create a password: ").strip()
    account_no = generate_account_number()
    bank_accounts[account_no] = {
        "name": name,
        "password": hash_password(password),
        "balance": 0.0,
        "transactions": []
    }
    print(f"Account created! Your account number is {account_no}")
    save_data()

def deposit():
    account_no = input("Enter account number: ").strip()
    password = input("Enter password: ").strip()
    if not authenticate(account_no, password):
        print("Authentication failed.")
        return
    try:
        amount = float(input("Enter amount to deposit: "))
        if amount <= 0:
            print("Amount must be positive.")
            return
        bank_accounts[account_no]["balance"] += amount
        bank_accounts[account_no]["transactions"].append(f"Deposited ₹{amount}")
        print("Deposit successful.")
        save_data()
    except ValueError:
        print("Invalid amount.")

def withdraw():
    account_no = input("Enter account number: ").strip()
    password = input("Enter password: ").strip()
    if not authenticate(account_no, password):
        print("Authentication failed.")
        return
    try:
        amount = float(input("Enter amount to withdraw: "))
        if amount <= 0:
            print("Amount must be positive.")
            return
        if bank_accounts[account_no]["balance"] < amount:
            print("Insufficient balance.")
            return
        bank_accounts[account_no]["balance"] -= amount
        bank_accounts[account_no]["transactions"].append(f"Withdrew ₹{amount}")
        print("Withdrawal successful.")
        save_data()
    except ValueError:
        print("Invalid amount.")

def check_balance():
    account_no = input("Enter account number: ").strip()
    password = input("Enter password: ").strip()
    if not authenticate(account_no, password):
        print("Authentication failed.")
        return
    balance = bank_accounts[account_no]["balance"]
    print(f"Current balance: ₹{balance:.2f}")

def view_transactions():
    account_no = input("Enter account number: ").strip()
    password = input("Enter password: ").strip()
    if not authenticate(account_no, password):
        print("Authentication failed.")
        return
    transactions = bank_accounts[account_no]["transactions"]
    if not transactions:
        print("No transactions found.")
    else:
        print("Transaction History:")
        for t in transactions:
            print(" -", t)

# ------------------------- Menu System -------------------------
def menu():
    load_data()
    while True:
        print("\n====== MINI BANK SYSTEM MENU ======")
        print("1. Create Account")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Check Balance")
        print("5. View Transactions")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            create_account()
        elif choice == "2":
            deposit()
        elif choice == "3":
            withdraw()
        elif choice == "4":
            check_balance()
        elif choice == "5":
            view_transactions()
        elif choice == "6":
            save_data()
            print("Thank you for using the Mini Bank System!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

# ------------------------- Start App -------------------------
if __name__ == "__main__":
    menu()
