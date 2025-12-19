"""
Module central du compilateur Mini-Pascal
Coordonne lexer, parser et AST
"""
from lexer import lexer, find_column
from parser_1 import parser
from errors import LexicalError, SyntaxError_
import ast_1

class PascalCompiler:
    def __init__(self):
        self.source_code = ""
        self.tokens = []
        self.ast = None
        self.errors = []
    
    def set_source(self, source_code):
        """Définit le code source à compiler"""
        self.source_code = source_code
        # Met à jour le texte source global pour le parser
        import parser_1
        parser_1.source_text = source_code
    
    def compile(self, source_code):
        """Exécute toutes les étapes de compilation"""
        self.source_code = source_code
        self.errors = []
        
        # Étape 1: Analyse lexicale
        tokens, lex_error = self.lexical_analysis()
        if lex_error:
            self.errors.append(f"Erreur lexicale: {lex_error}")
            return False
            
        # Étape 2: Analyse syntaxique
        ast, parse_error = self.syntactic_analysis()
        if parse_error:
            self.errors.append(f"Erreur syntaxique: {parse_error}")
            return False
            
        self.ast = ast
        return True
    
    def lexical_analysis(self):
        """Analyse lexicale - retourne des tokens avec informations de position"""
        try:
            lexer.input(self.source_code)
            tokens_list = []
            while True:
                tok = lexer.token()
                if not tok:
                    break
                # Calcul de la colonne
                col = find_column(self.source_code, tok)
                tokens_list.append({
                    'type': tok.type,
                    'value': tok.value,
                    'line': tok.lineno,
                    'column': col
                })
            return tokens_list, None
        except LexicalError as e:
            return None, str(e)
    
    def syntactic_analysis(self):
        """Analyse syntaxique et construction AST"""
        try:
            lexer.input(self.source_code)
            self.ast = parser.parse(self.source_code, lexer=lexer, debug=False)
            return self.ast, None
        except SyntaxError_ as e:
            return None, str(e)
        except Exception as e:
            return None, f"Erreur lors de l'analyse syntaxique: {str(e)}"
    
    def build_ast(self):
        """Construit et retourne la représentation textuelle de l'AST"""
        try:
            ast, error = self.syntactic_analysis()
            if error:
                return None, error
            if ast and hasattr(ast, 'to_tree_string'):
                return ast.to_tree_string(), None
            else:
                return None, "AST non disponible ou invalide"
        except Exception as e:
            return None, f"Erreur lors de la construction de l'AST: {str(e)}"
    
    def get_ast_tree(self):
        """Retourne la représentation textuelle de l'AST"""
        if self.ast and hasattr(self.ast, 'to_tree_string'):
            return self.ast.to_tree_string()
        return "AST non disponible"
    
    def get_ast_json(self):
        """Retourne l'AST en format JSON"""
        if self.ast and hasattr(self.ast, 'serialize'):
            return self.ast.serialize()
        return {}