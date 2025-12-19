# arbre syntaxique abstrait

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Union, Any
import json


"""Classe de base pour tous les nœuds AST"""
class ASTNode:
    
    def serialize(self):
        """Sérialise l'AST en dictionnaire JSON-friendly"""
        def process_value(value):
            if isinstance(value, ASTNode):
                return value.serialize()
            elif isinstance(value, list):
                return [process_value(item) for item in value if item is not None]
            elif isinstance(value, (int, float, str, bool)) or value is None:
                return value
            else:
                return str(value)
        
        result = {}
        for key, value in asdict(self).items():
            result[key] = process_value(value)
        return result
    
    def to_tree_string(self, level=0):
        """Convertit l'AST en représentation arborescente textuelle"""
        raise NotImplementedError("Chaque nœud doit implémenter cette méthode")

@dataclass
class Program(ASTNode):
    name: str
    block: 'Block'
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        result = f"{indent}Program(name='{self.name}')\n"
        if self.block:
            result += self.block.to_tree_string(level + 1)
        else:
            result += f"{indent}  Block: None\n"
        return result

@dataclass
class Block(ASTNode):
    consts: List['ConstDecl'] = field(default_factory=list)
    vars: List['VarDecl'] = field(default_factory=list)
    statements: List[Optional['Statement']] = field(default_factory=list)
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        result = f"{indent}Block:\n"
        
        if self.consts:
            result += f"{indent}  ConstDeclarations:\n"
            for const in self.consts:
                if const:
                    result += const.to_tree_string(level + 2)
        
        if self.vars:
            result += f"{indent}  VarDeclarations:\n"
            for var in self.vars:
                if var:
                    result += var.to_tree_string(level + 2)
        
        if self.statements:
            result += f"{indent}  Statements:\n"
            for stmt in self.statements:
                if stmt:
                    result += stmt.to_tree_string(level + 2)
                else:
                    result += f"{indent}    [Empty Statement]\n"
        
        return result

@dataclass
class ConstDecl(ASTNode):
    name: str
    value: 'Literal'
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        if self.value:
            return f"{indent}ConstDecl(name='{self.name}', value={self.value.value})\n"
        else:
            return f"{indent}ConstDecl(name='{self.name}', value=None)\n"

@dataclass
class VarDecl(ASTNode):
    name: str
    type: str
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        return f"{indent}VarDecl(name='{self.name}', type='{self.type}')\n"

class Statement(ASTNode):
    pass

class Expression(ASTNode):
    pass

@dataclass
class Assign(Statement):
    target: 'VarRef'
    value: Optional[Expression]
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        result = f"{indent}Assign:\n"
        result += f"{indent}  target:\n"
        if self.target:
            result += self.target.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        result += f"{indent}  value:\n"
        if self.value:
            result += self.value.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        return result

@dataclass
class If(Statement):
    condition: Expression
    then_stmt: Optional[Statement]
    else_stmt: Optional[Statement] = None
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        result = f"{indent}If:\n"
        result += f"{indent}  condition:\n"
        if self.condition:
            result += self.condition.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        result += f"{indent}  then:\n"
        if self.then_stmt:
            result += self.then_stmt.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        if self.else_stmt:
            result += f"{indent}  else:\n"
            result += self.else_stmt.to_tree_string(level + 2)
        return result

@dataclass
class While(Statement):
    condition: Expression
    body: Optional[Statement]
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        result = f"{indent}While:\n"
        result += f"{indent}  condition:\n"
        if self.condition:
            result += self.condition.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        result += f"{indent}  body:\n"
        if self.body:
            result += self.body.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        return result

@dataclass
class For(Statement):
    var: Optional['VarRef']
    start: Optional[Expression]
    direction: str
    end: Optional[Expression]
    body: Optional[Statement]
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        result = f"{indent}For(var='{self.var.name if self.var else None}', direction='{self.direction}'):\n"
        result += f"{indent}  start:\n"
        if self.start:
            result += self.start.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        result += f"{indent}  end:\n"
        if self.end:
            result += self.end.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        result += f"{indent}  body:\n"
        if self.body:
            result += self.body.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        return result

@dataclass
class Repeat(Statement):
    body: List[Optional['Statement']]
    condition: Optional[Expression]
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        result = f"{indent}Repeat:\n"
        result += f"{indent}  body:\n"
        for stmt in self.body:
            if stmt:
                result += stmt.to_tree_string(level + 2)
            else:
                result += f"{indent}    [Empty Statement]\n"
        result += f"{indent}  condition:\n"
        if self.condition:
            result += self.condition.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        return result

@dataclass
class Compound(Statement):
    statements: List[Optional['Statement']]
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        result = f"{indent}Compound:\n"
        for stmt in self.statements:
            if stmt:
                result += stmt.to_tree_string(level + 1)
            else:
                result += f"{indent}  [Empty Statement]\n"
        return result

@dataclass
class BinaryOp(Expression):
    op: str
    left: Optional['Expression']
    right: Optional['Expression']
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        result = f"{indent}BinaryOp(op='{self.op}'):\n"
        result += f"{indent}  left:\n"
        if self.left:
            result += self.left.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        result += f"{indent}  right:\n"
        if self.right:
            result += self.right.to_tree_string(level + 2)
        else:
            result += f"{indent}    None\n"
        return result

@dataclass
class UnaryOp(Expression):
    op: str
    operand: Optional['Expression']
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        result = f"{indent}UnaryOp(op='{self.op}'):\n"
        if self.operand:
            result += self.operand.to_tree_string(level + 1)
        else:
            result += f"{indent}  None\n"
        return result

@dataclass
class VarRef(Expression):
    name: str
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        return f"{indent}VarRef('{self.name}')\n"

@dataclass
class Literal(Expression):
    value: Any
    lineno: int = 0
    col: int = 0
    
    def to_tree_string(self, level=0):
        indent = "  " * level
        return f"{indent}Literal({self.value})\n"