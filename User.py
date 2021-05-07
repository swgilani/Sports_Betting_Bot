class User:
    def __init__(self,id,balance):
        self.id = id
        self.balance = balance


    def setBalance(self,balance):
        self.balance = balance

    def getBalance(self):
        return self.balance

    def getId(self):
        return self.id

    def deposit(self,balance):
        self.balance +=balance;

    def withdraw(self,balance):
        self.balance = self.balance - balance;


        