class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        if not isinstance(amount, (int, float)):
            raise TypeError("amount must be a number")
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance = self.balance + amount
        self.history.append(("deposit", amount))
        return self.balance

    def withdraw(self, amount):
        if not isinstance(amount, (int, float)):
            raise TypeError("amount must be a number")
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance = self.balance - amount
        self.history.append(("withdraw", amount))
        return self.balance

    def fee(self, amount):
        if not isinstance(amount, (int, float)):
            raise TypeError("amount must be a number")
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance = self.balance - amount
        self.history.append(("fee", amount))
        return self.balance
