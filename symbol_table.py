#table de synbole 

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        
    def add_symbol(self, name, type, value=None):
        self.symbols[name] = {'type': type, 'value': value}
    
    def get_symbol(self, name):
        return self.symbols.get(name)
    
    def exists(self, name):
        return name in self.symbols