import random
import json
import os
import hashlib
import getpass # For hiding password input
import datetime  # <-- Add this import


# --- Configuration ---
DATA_FILE = "banking_data.json"
INTEREST_RATE = 0.015 # Annual interest rate (e.g., 1.5%)

# --- Global Data Store ---
# This dictionary holds all our bank accounts.
# Key: account_number (string), Value: dictionary of account details
# Example: {'1001': {'name': 'Alice', 'balance': 1500.0, 'password_hash': '...', 'transactions': [...]}}
accounts = {}
next_account_number = 1001 # Used for generating new account numbers
 
# --- Utility Functions ---

def generate_account_number():
    """Creates a unique account number (simple sequential for this example)."""
    global next_account_number
    # NOTE: In a real system, especially with concurrent users, this needs a more robust
    # mechanism (like database sequences or UUIDs) to guarantee uniqueness.
    while str(next_account_number) in accounts:
        next_account_number += 1
    acc_num = str(next_account_number)
    next_account_number += 1
    return acc_num

def hash_password(password):
    """Hashes a password securely using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, provided_password):
    """Checks if the provided password matches the stored hash."""
    return stored_hash == hash_password(provided_password)

def get_timestamp():
    """Returns a formatted timestamp string for transactions."""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Nicer format


def format_currency(amount):
    """Formats a number as currency (e.g., $1,234.50)."""
    return f"${amount:,.2f}"

def record_transaction(acc_num, trans_type, amount, **details):
    """Adds a transaction record to an account's history."""
    if acc_num not in accounts:
        # This shouldn't happen if called correctly, but good to check
        print(f"Debug Error: Trying to record transaction for non-existent account {acc_num}")
        return

    transaction = {
        "timestamp": get_timestamp(),
        "type": trans_type,
        "amount": amount,
        **details # Merge any additional details (like fee, target_account)
    }
    accounts[acc_num]["transactions"].append(transaction)

def find_account(acc_num):
    """Quickly checks if an account exists and returns it, or None."""
    return accounts.get(acc_num)

def authenticate_user(acc_num):
    """Handles password verification for an account."""
    account = find_account(acc_num)
    if not account:
        print(f"Error: Account {acc_num} not found.")
        return None # Account doesn't exist

    # Check if password protection is even setup for this account
    if "password_hash" not in account:
        print("Account found, but no password set (older account or feature disabled?). Access granted.")
        return account # Allow access

    # Password check loop
    for attempt in range(3, 0, -1):
        password = getpass.getpass(f"Enter password for account {acc_num}: ")
        if verify_password(account["password_hash"], password):
            # print("Password correct.") # Maybe too noisy
            return account # Success! Return the account data
        else:
            print(f"Incorrect password. {attempt - 1} attempts left.")

    print("Authentication failed after 3 attempts.")
    return None # Failed auth

# --- Core Banking Operations ---

def create_new_account():
    """Guides the user through creating a new bank account."""
    print("\n--- Create New Account ---")
    
    # Step 1: Ask for account holder's full name
    name = input("Enter account holder's full name: ").strip()
    if not name:
        print("Account name cannot be blank.")
        return

    # Step 2: Set password
    password = ""
    while True:
        pwd1 = getpass.getpass("Set a password for this account: ")
        if not pwd1:
            print("Password cannot be empty.")
            continue
        pwd2 = getpass.getpass("Confirm password: ")
        if pwd1 == pwd2:
            password = pwd1
            break
        else:
            print("Passwords don't match. Try again.")

    # Step 3: Get initial deposit amount
    initial_deposit = 0.0
    while True:
        try:
            amount_str = input("Enter initial deposit amount ($0.00 or more): ")
            initial_deposit = float(amount_str)
            if initial_deposit < 0:
                print("Initial deposit cannot be negative.")
            else:
                break # Valid amount entered
        except ValueError:
            print("Invalid amount. Please enter a number (e.g., 50.00 or 0).")

    # Generate details and store
    acc_num = generate_account_number()
    password_hash = hash_password(password)

    accounts[acc_num] = {
        "name": name,
        "balance": initial_deposit,
        "password_hash": password_hash,
        "transactions": [] # Start with an empty transaction list
    }

    # Add the first transaction if there was an initial deposit
    if initial_deposit > 0:
        record_transaction(acc_num, "Initial Deposit", initial_deposit)

    print("-" * 30)
    print("Account successfully created!")
    print(f"  Holder: {name}")
    print(f"  Account Number: {acc_num}")
    print(f"  Balance: {format_currency(initial_deposit)}")
    print("-" * 30)
    save_banking_data() # Save changes


def make_deposit():
    """Handles depositing funds into an account."""
    print("\n--- Deposit Funds ---")
    acc_num = input("Enter the account number to deposit into: ").strip()
    account = authenticate_user(acc_num) # Checks existence and password

    if not account:
        return # Authentication failed or account not found

    # Get deposit amount
    while True:
        try:
            amount_str = input("Enter amount to deposit (must be positive): ")
            amount = float(amount_str)
            if amount > 0:
                break # Valid amount
            else:
                print("Deposit amount must be greater than zero.")
        except ValueError:
            print("Invalid amount. Please enter a number (e.g., 100.50).")

    # Update balance and record
    account["balance"] += amount
    record_transaction(acc_num, "Deposit", amount)

    print(f"\nDeposit of {format_currency(amount)} successful.")
    print(f"New balance for account {acc_num}: {format_currency(account['balance'])}")
    save_banking_data() # Save changes

def make_withdrawal():
    """Handles withdrawing funds from an account."""
    print("\n--- Withdraw Funds ---")
    acc_num = input("Enter the account number to withdraw from: ").strip()
    account = authenticate_user(acc_num) # Checks existence and password

    if not account:
        return

    # Get withdrawal amount
    while True:
        try:
            amount_str = input("Enter amount to withdraw (must be positive): ")
            amount = float(amount_str)
            if amount > 0:
                break # Valid amount
            else:
                print("Withdrawal amount must be greater than zero.")
        except ValueError:
            print("Invalid amount. Please enter a number (e.g., 50.00).")

    # Check for sufficient funds
    if amount > account["balance"]:
        print("\nError: Insufficient funds.")
        print(f"  Available: {format_currency(account['balance'])}")
        print(f"  Requested: {format_currency(amount)}")
    else:
        # Process withdrawal
        account["balance"] -= amount
        record_transaction(acc_num, "Withdrawal", amount) # Can add fee details here if needed

        print(f"\nWithdrawal of {format_currency(amount)} successful.")
        print(f"Remaining balance for account {acc_num}: {format_currency(account['balance'])}")
        save_banking_data() # Save changes

def display_balance():
    """Shows the current balance for an account."""
    print("\n--- Check Account Balance ---")
    acc_num = input("Enter the account number: ").strip()
    account = authenticate_user(acc_num) # Checks existence and password

    if not account:
        return

    print("-" * 30)
    print(f"Account Holder: {account['name']}")
    print(f"Account Number: {acc_num}")
    print(f"Current Balance: {format_currency(account['balance'])}")
    print("-" * 30)

def display_transaction_history():
    """Shows the list of transactions for an account."""
    print("\n--- Account Transaction History ---")
    acc_num = input("Enter the account number: ").strip()
    account = authenticate_user(acc_num) # Checks existence and password

    if not account:
        return

    print("-" * 70)
    print(f"History for Account: {acc_num} ({account['name']})")
    print("-" * 70)

    transactions = account.get("transactions", []) # Use .get for safety
    if not transactions:
        print("No transactions recorded for this account.")
    else:
        # Header
        print(f"{'Timestamp':<20} | {'Type':<18} | {'Amount':<15} | Details")
        print("-" * 70)
        # Transaction rows
        for tx in transactions:
            details = []
            if tx["type"] == "Withdrawal" and tx.get("fee", 0.0) > 0:
                 details.append(f"Fee: {format_currency(tx['fee'])}")
            if tx["type"] == "Transfer Sent":
                 details.append(f"To: {tx.get('to_account', 'N/A')}")
            if tx["type"] == "Transfer Received":
                 details.append(f"From: {tx.get('from_account', 'N/A')}")
            if tx["type"] == "Interest Applied":
                 # Calculate rate from amount and balance before interest (approximate)
                 # Note: This calculation is tricky without storing the balance *before* interest.
                 # For simplicity, maybe just show the rate constant if needed, or omit.
                 details.append(f"Rate: {INTEREST_RATE*100:.2f}% (annual)")

            details_str = ", ".join(details)
            print(f"{tx['timestamp']:<20} | {tx['type']:<18} | {format_currency(tx['amount']):<15} | {details_str}")

    print("-" * 70)


# --- Bonus Feature Functions ---

def transfer_funds():
    """Allows transferring money between two accounts."""
    print("\n--- Transfer Funds ---")
    # Get source account and authenticate
    source_acc_num = input("Enter YOUR account number (transferring FROM): ").strip()
    source_account = authenticate_user(source_acc_num)
    if not source_account:
        return # Auth failed or account not found

    # Get destination account
    dest_acc_num = input("Enter the recipient's account number (transferring TO): ").strip()
    if source_acc_num == dest_acc_num:
        print("Error: Cannot transfer funds to the same account.")
        return
    dest_account = find_account(dest_acc_num)
    if not dest_account:
        print(f"Error: Recipient account {dest_acc_num} does not exist.")
        return

    # Get transfer amount
    while True:
        try:
            amount_str = input("Enter amount to transfer (must be positive): ")
            amount = float(amount_str)
            if amount > 0:
                break # Valid amount
            else:
                print("Transfer amount must be greater than zero.")
        except ValueError:
            print("Invalid amount. Please enter a number (e.g., 25.00).")

    # Check funds in source account
    if amount > source_account["balance"]:
        print("\nError: Insufficient funds to complete transfer.")
        print(f"  Available: {format_currency(source_account['balance'])}")
        print(f"  Requested: {format_currency(amount)}")
        return

    # Perform the transfer
    source_account["balance"] -= amount
    dest_account["balance"] += amount

    # Record in both account histories
    record_transaction(source_acc_num, "Transfer Sent", amount, to_account=dest_acc_num)
    record_transaction(dest_acc_num, "Transfer Received", amount, from_account=source_acc_num)

    print("\nTransfer successful!")
    print(f"  {format_currency(amount)} transferred from {source_acc_num} to {dest_acc_num}")
    print(f"  Your new balance: {format_currency(source_account['balance'])}")
    save_banking_data() # Save changes

def apply_interest_to_all_accounts():
    """Calculates and applies interest to all eligible accounts."""
    print("\n--- Apply Annual Interest ---")
    if not accounts:
        print("No accounts in the system to apply interest to.")
        return

    applied_count = 0
    for acc_num, account_data in accounts.items():
        if account_data["balance"] > 0:
            interest_earned = round(account_data["balance"] * INTEREST_RATE, 2) # Calculate and round
            if interest_earned > 0: # Only apply if interest is actually earned
                account_data["balance"] += interest_earned
                record_transaction(acc_num, "Interest Applied", interest_earned)
                print(f"Applied {format_currency(interest_earned)} interest to account {acc_num}. New balance: {format_currency(account_data['balance'])}")
                applied_count += 1

    if applied_count > 0:
        print(f"\nInterest applied to {applied_count} account(s).")
        save_banking_data()
    else:
        print("\nNo interest was applied (no accounts had a positive balance).")


# --- Data Persistence ---

def save_banking_data():
    """Saves the current state of accounts and the next account number to a file."""
    global accounts, next_account_number
    data_to_save = {
        "accounts": accounts,
        "next_account_number": next_account_number
    }
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=4) # Use indent for readability
        # print("Data saved.") # Keep it quiet unless there's an error
    except IOError as e:
        print(f"\nCRITICAL ERROR: Could not save data to {DATA_FILE}! Changes might be lost. Error: {e}")
    except Exception as e:
         print(f"\nCRITICAL ERROR: An unexpected error occurred while saving data: {e}")


def load_banking_data():
    """Loads data from the file when the application starts."""
    global accounts, next_account_number
    if not os.path.exists(DATA_FILE):
        print(f"Welcome! Data file ({DATA_FILE}) not found. Starting fresh.")
        accounts = {}
        next_account_number = 1001 # Start from the beginning
        return

    print(f"Loading data from {DATA_FILE}...")
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Basic validation
            if isinstance(data, dict) and "accounts" in data and "next_account_number" in data:
                accounts = data["accounts"]
                next_account_number = data["next_account_number"]
                # Simple fixup: Ensure all accounts have a transaction list
                for acc_data in accounts.values():
                     if "transactions" not in acc_data or not isinstance(acc_data["transactions"], list):
                         acc_data["transactions"] = []
                     # Add password hash field if missing from older data? Optional.
                     # if "password_hash" not in acc_data:
                     #    acc_data["password_hash"] = None # Or prompt to set one?

                print("Data loaded successfully.")
            else:
                 print(f"Warning: Data file format seems incorrect. Starting with empty data.")
                 accounts = {}
                 next_account_number = 1001
    except json.JSONDecodeError:
        print(f"Warning: Could not understand data in {DATA_FILE}. It might be corrupted. Starting with empty data.")
        accounts = {}
        next_account_number = 1001
    except IOError as e:
        print(f"Warning: Could not read data file {DATA_FILE}. Error: {e}. Starting with empty data.")
        accounts = {}
        next_account_number = 1001
    except Exception as e:
        print(f"Warning: An unexpected error occurred loading data: {e}. Starting with empty data.")
        accounts = {}
        next_account_number = 1001


# --- Main Application Loop ---

def show_menu():
    """Prints the main menu."""
    print("\n===== Mini Banking Menu =====")
    print("1. Create Account")
    print("2. Deposit Funds")
    print("3. Withdraw Funds")
    print("4. Check Balance")
    print("5. View Transaction History")
    print("6. Transfer Funds")
    print("7. Apply Interest (Admin)") # Clarify purpose
    print("8. Exit")
    print("=============================")

def run_bank():
    """Starts and runs the banking application."""
    load_banking_data() # Load data first

    while True:
        show_menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == '1':
            create_new_account()
        elif choice == '2':
            make_deposit()
        elif choice == '3':
            make_withdrawal()
        elif choice == '4':
            display_balance()
        elif choice == '5':
            display_transaction_history()
        elif choice == '6':
            transfer_funds()
        elif choice == '7':
            apply_interest_to_all_accounts()
        elif choice == '8':
            print("\nExiting application. Saving data...")
            # Data is already saved after each transaction, but an extra save doesn't hurt.
            save_banking_data()
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 8.")

        # Pause briefly so the user can see the output before the menu reappears
        input("\nPress Enter to continue...")
        # Add a screen clear for better UX (optional, platform dependent)
        # os.system('cls' if os.name == 'nt' else 'clear') # Uncomment for screen clearing

# --- Run the Application ---
if __name__ == "__main__":
    run_bank()