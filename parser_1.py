import ply.yacc as yacc
from lexer import tokens, lexer, find_column
from ast_1 import *
from errors import SyntaxError_, format_error_line

# Stockage du texte source pour messages d'erreur
source_text = ''

# Priorité des opérateurs (corrigée)
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'EQUAL', 'NEQ', 'LT', 'LEQ', 'GT', 'GEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIVIDE', 'DIV', 'MOD'),
    ('right', 'UMINUS'),
)

# Règles de grammaire

def p_program(p):
    '''program : PROGRAM ID SEMI block DOT'''
    p[0] = Program(name=p[2], block=p[4], lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))

def p_block(p):
    '''block : declarations BEGIN statements END'''
    consts = p[1].get('consts', [])
    vars_ = p[1].get('vars', [])
    stmts = p[3]
    p[0] = Block(consts=consts, vars=vars_, statements=stmts, 
                lineno=p.lineno(2), col=find_column(source_text, p.slice[2]))

def p_declarations(p):
    '''declarations : declarations var_decl
                    | declarations const_decl
                    | empty'''
    if len(p) == 3:
        decls = p[1] if p[1] else {'vars': [], 'consts': []}
        if isinstance(p[2], list):  # var_decl retourne une liste
            decls['vars'].extend(p[2])
        else:  # const_decl retourne un ConstDecl
            decls['consts'].append(p[2])
        p[0] = decls
    else:
        p[0] = {'vars': [], 'consts': []}

def p_const_decl(p):
    '''const_decl : CONST ID EQUAL literal SEMI'''
    p[0] = ConstDecl(name=p[2], value=p[4], 
                     lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))

def p_var_decl(p):
    '''var_decl : VAR id_list COLON type SEMI'''
    vars_list = []
    for name in p[2]:
        vars_list.append(VarDecl(name=name, type=p[4], 
                               lineno=p.lineno(1), col=find_column(source_text, p.slice[1])))
    p[0] = vars_list

def p_id_list(p):
    '''id_list : ID
               | id_list COMMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_type(p):
    '''type : INTEGER
            | REAL
            | BOOLEAN'''
    p[0] = p[1].lower()


def p_statements(p):
    '''statements : statement
                  | statements SEMI statement'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        statements = p[1] if p[1] is not None else []
        if p[3] is not None:
            statements.append(p[3])
        p[0] = statements

def p_statement(p):
    '''statement : assignment
                 | if_stmt
                 | while_stmt
                 | for_stmt
                 | repeat_stmt
                 | compound_stmt
                 | empty_stmt'''
    p[0] = p[1]

# Ajouter une règle pour un statement vide (sans erreur)
def p_empty_stmt(p):
    '''empty_stmt :'''
    p[0] = None

def p_assignment(p):
    '''assignment : ID ASSIGN expression'''
    var_ref = VarRef(name=p[1], lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))
    p[0] = Assign(target=var_ref, value=p[3], 
                 lineno=p.lineno(2), col=find_column(source_text, p.slice[2]))

def p_if_stmt(p):
    '''if_stmt : IF expression THEN statement
               | IF expression THEN statement ELSE statement'''
    if len(p) == 5:
        p[0] = If(condition=p[2], then_stmt=p[4], 
                  lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))
    else:
        p[0] = If(condition=p[2], then_stmt=p[4], else_stmt=p[6],
                  lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))

def p_while_stmt(p):
    '''while_stmt : WHILE expression DO statement'''
    p[0] = While(condition=p[2], body=p[4],
                 lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))

def p_for_stmt(p):
    '''for_stmt : FOR ID ASSIGN expression TO expression DO statement
                | FOR ID ASSIGN expression DOWNTO expression DO statement'''
    var_ref = VarRef(name=p[2], lineno=p.lineno(2), col=find_column(source_text, p.slice[2]))
    direction = 'to' if p[5].lower() == 'to' else 'downto'
    p[0] = For(var=var_ref, start=p[4], direction=direction, end=p[6], body=p[8],
               lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))

def p_repeat_stmt(p):
    '''repeat_stmt : REPEAT statements UNTIL expression'''
    p[0] = Repeat(body=p[2], condition=p[4],
                  lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))

def p_compound_stmt(p):
    '''compound_stmt : BEGIN statements END'''
    p[0] = Compound(statements=p[2],
                    lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))

# Expressions - version simplifiée pour éviter les conflits

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULT expression
                  | expression DIVIDE expression
                  | expression DIV expression
                  | expression MOD expression'''
    p[0] = BinaryOp(op=p[2], left=p[1], right=p[3],
                    lineno=p.lineno(2), col=find_column(source_text, p.slice[2]))

def p_expression_comparison(p):
    '''expression : expression EQUAL expression
                  | expression NEQ expression
                  | expression LT expression
                  | expression LEQ expression
                  | expression GT expression
                  | expression GEQ expression
                  | expression AND expression
                  | expression OR expression'''
    p[0] = BinaryOp(op=p[2], left=p[1], right=p[3],
                    lineno=p.lineno(2), col=find_column(source_text, p.slice[2]))

def p_expression_unary(p):
    '''expression : NOT expression
                  | MINUS expression %prec UMINUS'''
    op = 'UMINUS' if p[1] == '-' else p[1]
    p[0] = UnaryOp(op=op, operand=p[2],
                   lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_literal(p):
    '''expression : INT_CONST
                  | REAL_CONST
                  | BOOL_CONST'''
    p[0] = Literal(value=p[1], lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))

def p_literal(p):
    '''literal : INT_CONST
               | REAL_CONST
               | BOOL_CONST'''
    p[0] = Literal(value=p[1], lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))

def p_expression_var(p):
    '''expression : ID'''
    p[0] = VarRef(name=p[1], lineno=p.lineno(1), col=find_column(source_text, p.slice[1]))

def p_empty(p):
    '''empty :'''
    p[0] = None

def p_error(p):
    if p:
        col = find_column(source_text, p)
        err_line = format_error_line(source_text, p.lineno, col)
        msg = f"Erreur syntaxique: caractère inattendu '{p.value}' à la ligne {p.lineno}, colonne {col}\n{err_line}"
    else:
        msg = "Erreur syntaxique: fin de fichier inattendue"
    raise SyntaxError_(msg)

# Construire le parser avec débogage activé
parser = yacc.yacc(debug=False, write_tables=False)