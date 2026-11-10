class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, name, qty):
        if name in self.items:
            self.items[name] = self.items[name] + qty
        else:
            self.items[name] = qty

    def remove(self, name, qty):
        if name in self.items:
            if self.items[name] >= qty:
                self.items[name] = self.items[name] - qty
                if self.items[name] == 0:
                    del self.items[name]
                return True
            else:
                return False
        else:
            return False

    def in_stock(self, name):
        if name in self.items:
            return True
        else:
            return False

    def low_stock(self, threshold):
        result = []
        for name in self.items:
            if self.items[name] < threshold:
                result.append(name)
        return sorted(result)
