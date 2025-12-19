import ply.lex as lex
from errors import LexicalError

# Liste complète des tokens
tokens = (
    'PROGRAM', 'VAR', 'CONST', 'INTEGER', 'REAL', 'BOOLEAN',
    'IF', 'THEN', 'ELSE', 'WHILE', 'DO', 'FOR', 'TO', 'DOWNTO', 
    'REPEAT', 'UNTIL', 'DIV', 'MOD', 'AND', 'OR', 'NOT',
    'ID', 'INT_CONST', 'REAL_CONST', 'BOOL_CONST',
    'PLUS', 'MINUS', 'MULT', 'DIVIDE', 'ASSIGN',
    'EQUAL', 'NEQ', 'LT', 'GT', 'LEQ', 'GEQ',
    'LPAREN', 'RPAREN', 'SEMI', 'COLON', 'COMMA', 'DOT',
    'BEGIN', 'END'
)

# Mots-clés Pascal
reserved = {
    'program': 'PROGRAM', 
    'var': 'VAR', 
    'const': 'CONST',
    'integer': 'INTEGER', 
    'real': 'REAL', 
    'boolean': 'BOOLEAN',
    'if': 'IF', 
    'then': 'THEN', 
    'else': 'ELSE',
    'while': 'WHILE', 
    'do': 'DO', 
    'for': 'FOR',
    'to': 'TO', 
    'downto': 'DOWNTO', 
    'repeat': 'REPEAT',
    'until': 'UNTIL', 
    'div': 'DIV', 
    'mod': 'MOD',
    'and': 'AND', 
    'or': 'OR', 
    'not': 'NOT',
    'begin': 'BEGIN', 
    'end': 'END',
    'true': 'BOOL_CONST', 
    'false': 'BOOL_CONST'
}

# Expressions régulières simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r':='
t_EQUAL = r'='
t_NEQ = r'<>'
t_LT = r'<'
t_GT = r'>'
t_LEQ = r'<='
t_GEQ = r'>='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMI = r';'
t_COLON = r':'
t_COMMA = r','
t_DOT = r'\.'

t_ignore = ' \t'

# Règle pour les commentaires (simplifiée)
def t_COMMENT(t):
    r'\{[^}]*\}'
    t.lexer.lineno += t.value.count('\n')
    return None

def t_REAL_CONST(t):
    r'\d+\.\d+'
    try:
        t.value = float(t.value)
    except ValueError:
        raise LexicalError(f"Valeur réelle invalide: {t.value}", t.lineno, find_column(t.lexer.lexdata, t))
    return t

def t_INT_CONST(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        raise LexicalError(f"Valeur entière invalide: {t.value}", t.lineno, find_column(t.lexer.lexdata, t))
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'ID')
    if t.type == 'BOOL_CONST':
        t.value = (t.value.lower() == 'true')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

"""Calcule la colonne précise d'un token"""
def find_column(input_text, token):
    last_cr = input_text.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = -1
    column = token.lexpos - last_cr
    return column

def t_error(t):
    col = find_column(t.lexer.lexdata, t)
    raise LexicalError(
        f"Caractère non reconnu '{t.value[0]}' à la ligne {t.lineno}, colonne {col}",
        t.lineno, col
    )

# Construire le lexer
lexer = lex.lex()