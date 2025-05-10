#--------------------------Mini Bank Application--------------------------------
#Account Creation 
bank_account={}
account_number=10001
def generate_account():
    global account_number
    Account_No = account_number
    account_number += 1
    return Account_No
def create_account():
    name=input("Enter Your Name : ")
    password = input("enter your password: ")
    Account_No = generate_account()
    bank_account[Account_No] = {"name": name,"password":password, "balance":0, "transactions":[]}
    print(f"Account Created for {name}, Your Account {Account_No}")

#Deposit Money
def Deposit():
    Account_No=int(input("enter your account no: "))
    if Account_No in bank_account:
        try:
            amount = float(input("enter ammount to deposit: "))
            if amount > 0:
                bank_account[Account_No]["balance"] += amount
                bank_account[Account_No]["transactions"].append(f"Deposited{amount}")
                print("Deposit Succesfully.")
            else:
                print("amount must be possitive")
        except ValueError:
            print("invalid amount.please enter a number")
    else:
        print("account not found.")

#withdraw money
def withdraw():
    Account_No=input("enter your account number: ")
    if Account_No in bank_account:
        try:
            amount = float(input("enter ammount to deposit :"))
            if amount > 0:
                if bank_account[Account_No]["balance"] >= amount:
                    bank_account[Account_No]["balance"] -= amount
                    bank_account[Account_No]["transactions"].append(f"withdraw{amount}")
                    print("withdraw successful.")
                else:
                    print("insufficient balance")
            else:
                print("amount must be possitive")
        except ValueError:
            print("invalid amount.please enter a number")
    else:
        print("account not found")

#check balance
def check_balance():
     Account_No=int(input("enter your account number : "))
     if Account_No in bank_account:
         balance=bank_account[Account_No]["balance"]
         print(f"current balance:{balance}")
     else:
         print("account not found")

#transactions
def view_transactions():
    Account_No=int(input("enter your account number : "))
    if Account_No in bank_account:
        print("Transaction History")
        for t in bank_account[Account_No]["transactions"]:
            print("-", t)

def save_to_file():
    with open("bank_data.txt", "w")as file:
        for Account_No, details in bank_account.items():
            file.write(f"{Account_No},{details["name"]},{details["password"]},{details["balance"]}\n")
            for txt in details["transactions"]:
                file.write(f"transactions:{txt}\n")
                print("data saved Succesfully")

 
#========Menu========
def menu():
    while True:
        print("\n-----MINI BANK SYSTEM MENU-----")
        print("1. creat account")
        print("2. deposit money")
        print("3. withdraw money")
        print("4. check balance")
        print("5. transaction history")
        print("6. Exit")
        choice=input("enter your choice 1-6 : ")
        if choice == "1":
            create_account()
        elif choice == "2":
            Deposit()
        elif choice == "3":
            withdraw()
        elif choice == "4":
            check_balance()
        elif choice == "5":
            view_transactions()
        elif choice == "6":
            save_to_file()
            print("thank you for using the mini bank system")
            break
        else:
            print("invalid chice. please select a number 1 to 6.")
menu()

        

        
        


