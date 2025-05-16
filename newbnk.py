import json
import os
import getpass
from datetime import datetime


DATA_FILE = "bank_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"users": {}}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def hash_password(password):
    # For simplicity, use a simple hash - do NOT use this in real apps
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


class Transaction:
    def __init__(self, type_, amount, date=None, description=""):
        self.type = type_
        self.amount = amount
        self.date = date if date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.description = description

    def to_dict(self):
        return {
            "type": self.type,
            "amount": self.amount,
            "date": self.date,
            "description": self.description,
        }


class Account:
    def __init__(self, account_type, balance=0.0, transactions=None):
        self.account_type = account_type
        self.balance = balance
        self.transactions = transactions or []

    def deposit(self, amount):
        self.balance += amount
        self.transactions.append(Transaction("Deposit", amount).to_dict())

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.transactions.append(Transaction("Withdrawal", amount).to_dict())

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction.to_dict())

    def to_dict(self):
        return {
            "account_type": self.account_type,
            "balance": self.balance,
            "transactions": self.transactions,
        }

    @staticmethod
    def from_dict(data):
        return Account(
            account_type=data["account_type"],
            balance=data["balance"],
            transactions=data.get("transactions", []),
        )


class User:
    def __init__(self, username, password_hash, accounts=None, loans=None):
        self.username = username
        self.password_hash = password_hash
        self.accounts = accounts or {}
        self.loans = loans or []

    def check_password(self, password):
        return self.password_hash == hash_password(password)

    def add_account(self, account_type):
        if account_type in self.accounts:
            raise ValueError("Account already exists")
        self.accounts[account_type] = Account(account_type)

    def get_account(self, account_type):
        if account_type not in self.accounts:
            raise ValueError("Account does not exist")
        return self.accounts[account_type]

    def apply_loan(self, amount, interest_rate=5.0):
        loan = {
            "principal": amount,
            "interest_rate": interest_rate,
            "balance": amount,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        self.loans.append(loan)
        # Deposit loan amount to checking account by default
        self.get_account("checking").deposit(amount)

    def repay_loan(self, loan_index, amount):
        if loan_index >= len(self.loans) or loan_index < 0:
            raise IndexError("Invalid loan index")
        loan = self.loans[loan_index]
        if amount > self.get_account("checking").balance:
            raise ValueError("Insufficient funds to repay")
        repay_amount = min(amount, loan["balance"])
        self.get_account("checking").withdraw(repay_amount)
        loan["balance"] -= repay_amount
        if loan["balance"] <= 0:
            print("Loan fully repaid!")
            self.loans.pop(loan_index)

    def to_dict(self):
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "accounts": {k: v.to_dict() for k, v in self.accounts.items()},
            "loans": self.loans,
        }

    @staticmethod
    def from_dict(data):
        accounts = {k: Account.from_dict(v) for k, v in data.get("accounts", {}).items()}
        return User(
            username=data["username"],
            password_hash=data["password_hash"],
            accounts=accounts,
            loans=data.get("loans", []),
        )


class BankingApp:
    def __init__(self):
        self.data = load_data()
        self.current_user = None

    def register(self):
        print("\n=== Register ===")
        username = input("Enter username: ").strip()
        if username in self.data["users"]:
            print("Username already exists.")
            return
        password = getpass.getpass("Enter password: ").strip()
        password_confirm = getpass.getpass("Confirm password: ").strip()
        if password != password_confirm:
            print("Passwords do not match.")
            return
        user = User(username, hash_password(password))
        # Create default checking and savings accounts
        user.add_account("checking")
        user.add_account("savings")
        self.data["users"][username] = user.to_dict()
        save_data(self.data)
        print(f"User '{username}' registered successfully!")

    def login(self):
        print("\n=== Login ===")
        username = input("Enter username: ").strip()
        if username not in self.data["users"]:
            print("User not found.")
            return
        password = getpass.getpass("Enter password: ").strip()
        user = User.from_dict(self.data["users"][username])
        if user.check_password(password):
            self.current_user = user
            print(f"Welcome, {username}!")
            self.user_menu()
        else:
            print("Incorrect password.")

    def user_menu(self):
        while True:
            print("\n=== User Menu ===")
            print("1. View accounts")
            print("2. Deposit")
            print("3. Withdraw")
            print("4. Transfer between accounts")
            print("5. View transaction history")
            print("6. Apply for loan")
            print("7. View loans")
            print("8. Repay loan")
            print("9. Logout")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                self.view_accounts()
            elif choice == "2":
                self.deposit()
            elif choice == "3":
                self.withdraw()
            elif choice == "4":
                self.transfer()
            elif choice == "5":
                self.view_transactions()
            elif choice == "6":
                self.apply_loan()
            elif choice == "7":
                self.view_loans()
            elif choice == "8":
                self.repay_loan()
            elif choice == "9":
                self.logout()
                break
            else:
                print("Invalid option.")

    def view_accounts(self):
        print("\n=== Accounts ===")
        for account_type, account in self.current_user.accounts.items():
            print(f"{account_type.capitalize()}: ${account.balance:.2f}")

    def deposit(self):
        print("\n=== Deposit ===")
        account_type = input("Account (checking/savings): ").strip().lower()
        if account_type not in self.current_user.accounts:
            print("Invalid account.")
            return
        try:
            amount = float(input("Amount to deposit: "))
            if amount <= 0:
                print("Amount must be positive.")
                return
            self.current_user.get_account(account_type).deposit(amount)
            self.save_current_user()
            print(f"Deposited ${amount:.2f} into {account_type} account.")
        except ValueError:
            print("Invalid amount.")

    def withdraw(self):
        print("\n=== Withdraw ===")
        account_type = input("Account (checking/savings): ").strip().lower()
        if account_type not in self.current_user.accounts:
            print("Invalid account.")
            return
        try:
            amount = float(input("Amount to withdraw: "))
            account = self.current_user.get_account(account_type)
            account.withdraw(amount)
            self.save_current_user()
            print(f"Withdrew ${amount:.2f} from {account_type} account.")
        except ValueError as ve:
            print(f"Error: {ve}")

    def transfer(self):
        print("\n=== Transfer Between Accounts ===")
        from_acc = input("From account (checking/savings): ").strip().lower()
        to_acc = input("To account (checking/savings): ").strip().lower()
        if from_acc not in self.current_user.accounts or to_acc not in self.current_user.accounts:
            print("Invalid account(s).")
            return
        if from_acc == to_acc:
            print("Choose different accounts for transfer.")
            return
        try:
            amount = float(input("Amount to transfer: "))
            from_account = self.current_user.get_account(from_acc)
            to_account = self.current_user.get_account(to_acc)
            from_account.withdraw(amount)
            to_account.deposit(amount)
            # Add transfer transactions
            from_account.add_transaction(Transaction("Transfer Out", amount, description=f"To {to_acc} account"))
            to_account.add_transaction(Transaction("Transfer In", amount, description=f"From {from_acc} account"))
            self.save_current_user()
            print(f"Transferred ${amount:.2f} from {from_acc} to {to_acc}.")
        except ValueError as ve:
            print(f"Error: {ve}")

    def view_transactions(self):
        print("\n=== Transaction History ===")
        account_type = input("Account (checking/savings): ").strip().lower()
        if account_type not in self.current_user.accounts:
            print("Invalid account.")
            return
        account = self.current_user.get_account(account_type)
        if not account.transactions:
            print("No transactions.")
            return
        for tr in account.transactions:
            print(f"{tr['date']} - {tr['type']}: ${tr['amount']:.2f} {tr['description']}")

    def apply_loan(self):
        print("\n=== Apply for Loan ===")
        try:
            amount = float(input("Loan amount: "))
            if amount <= 0:
                print("Amount must be positive.")
                return
            self.current_user.apply_loan(amount)
            self.save_current_user()
            print(f"Loan of ${amount:.2f} approved and added to your checking account.")
        except ValueError as ve:
            print(f"Error: {ve}")

    def view_loans(self):
        print("\n=== Your Loans ===")
        if not self.current_user.loans:
            print("No active loans.")
            return
        for idx, loan in enumerate(self.current_user.loans):
            print(f"Loan #{idx + 1}: Principal: ${loan['principal']:.2f}, Balance: ${loan['balance']:.2f}, Interest Rate: {loan['interest_rate']}%")

    def repay_loan(self):
        print("\n=== Repay Loan ===")
        self.view_loans()
        if not self.current_user.loans:
            return
        try:
            loan_num = int(input("Select loan number to repay: "))
            loan_index = loan_num - 1
            amount = float(input("Amount to repay: "))
            self.current_user.repay_loan(loan_index, amount)
            self.save_current_user()
            print(f"Repayed ${amount:.2f} on loan #{loan_num}.")
        except (ValueError, IndexError) as e:
            print(f"Error: {e}")

    def logout(self):
        print(f"Goodbye, {self.current_user.username}!")
        self.current_user = None

    def save_current_user(self):
        self.data["users"][self.current_user.username] = self.current_user.to_dict()
        save_data(self.data)

    def main_menu(self):
        while True:
            print("\n=== Banking App Main Menu ===")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                self.register()
            elif choice == "2":
                self.login()
            elif choice == "3":
                print("Thank you for using the banking app!")
                break
            else:
                print("Invalid option.")


if __name__ == "__main__":
    app = BankingApp()
    app.main_menu()

