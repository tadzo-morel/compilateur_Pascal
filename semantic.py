#Analyse semantique

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.errors = []
        self.symbol_table = SymbolTable()
        
    def analyze(self):
        self.visit(self.ast)
        return self.errors
    
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def visit_Program(self, node):
        self.visit(node.block)
    
    def visit_Block(self, node):
        for const in node.consts:
            self.visit(const)
        for var in node.vars:
            self.visit(var)
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_VarDecl(self, node):
        if self.symbol_table.exists(node.name):
            self.errors.append(f"Variable déjà déclarée: {node.name}")
        else:
            self.symbol_table.add_symbol(node.name, node.type)
    
    # ... autres méthodes de visite