# Gestion des erreurs lexicales et syntaxiques
class LexicalError(Exception):
    def __init__(self, message, lineno=None, col=None):
        super().__init__(message)
        self.lineno = lineno
        self.col = col

class SyntaxError_(Exception):
    def __init__(self, message, lineno=None, col=None):
        super().__init__(message)
        self.lineno = lineno
        self.col = col

"""Formate une ligne avec marqueur de position d'erreur"""
def format_error_line(source, lineno, col): 
    lines = source.split('\n')
    if 0 < lineno <= len(lines):
        line_text = lines[lineno - 1]
        marker = ' ' * (col - 1) + '^'
        return f"{line_text}\n{marker}"
    return ''