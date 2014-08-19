import sys

EOF = '\0'
NEWLINE = '\n'
STRING_DELIMITERS = ['"', "'"]
NUMBER = 'Number'
STRING = 'String'
IDENTIFIER = 'Identifier'
KEYWORD = 'Keyword'
SYMBOL = 'Symbol'
SYMBOLS_PERMITTED = list('+-*/=<>!%;,')
OPEN_PARENS = '('
CLOSE_PARENS = ')'
OPEN_BRACKET = '{'
CLOSE_BRACKET = '}'
EQUAL = '=='
DIFF = '!='
BOOLEAN_VALUES = ['true', 'false']
IF = 'if'
ELSE = 'else'
WHILE = 'while'
BOOL_OR = 'or'
BOOL_AND = 'and'
BOOL_NOT = 'not'
FUNCTION = 'function'
RETURN = 'return'
PRINT = 'print'
READ = 'read'
KEYWORDS = {'if', 'else', 'while', 'or', 
    'and', 'not', 'function', 'return',
    'print', 'read'
}


class Token():
    def __init__(self, val, type):
        self.value = val
        self.type = type
    
    def is_addop(self):
        return self.value in ['+', '-']

    def is_mulop(self):
        return self.value in ['*', '/', '%']

    def is_equop(self):
        return self.value in ['==', '!=']

    def is_relop(self):
        return self.value in ['>', '>=', '<', '<=']


class Lexer():
    def __init__(self, code):
        self.index = 0
        self.code = code
        self.len = len(code)
        self.line = 1
        self.column = 1
        self.char = self.get_char()
    
    def get_char(self):
        if self.index >= self.len:
            return EOF
        char = self.code[self.index]
        self.column += 1
        self.index += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        return char

    def issymbol(self, c):
        return c in SYMBOLS_PERMITTED

    def next_char(self):
        self.char = self.get_char()

    def skip_whitespaces(self):
        while self.char.isspace():
            self.next_char()

    def error(self, msg):
        line = self.line
        column = self.column
        sys.exit('Error: {} at line {}, column {}'.format(msg, line, column))

    def get_number(self):
        num = ''
        while self.char.isdigit():
            num += self.char
            self.next_char()
        if self.char.isalpha():
            self.error('Invalid syntax')
        tok = Token(int(num), NUMBER)
        return tok

    def get_name(self):
        name = self.char
        self.next_char()
        while self.char.isalnum():
            name += self.char
            self.next_char()
        if name in KEYWORDS:
            tok = Token(name, KEYWORD)
        else:
            tok = Token(name, IDENTIFIER)
        return tok

    def get_string(self, delimiter):
        string_value = ''
        self.next_char()
        while self.char != delimiter:
            if self.char == EOF:
                self.error('String not properly closed')
            string_value += self.char
            self.next_char()
        self.next_char()
        return Token(string_value, STRING)

    def get_symbol(self):
        symbol = ''
        while self.issymbol(self.char):
            symbol += self.char
            self.next_char()
        tok = Token(symbol, SYMBOL)
        return tok

    def get_token(self):
        self.skip_whitespaces()
        tok = None
        if self.char.isdigit():
            tok = self.get_number()
        elif self.char.isalpha():
            tok = self.get_name()
        elif self.issymbol(self.char):
            tok = self.get_symbol()
        elif self.char in STRING_DELIMITERS:
            tok = self.get_string(self.char)
        elif self.char == OPEN_PARENS:
            tok = Token(self.char, OPEN_PARENS)
            self.next_char()
        elif self.char == CLOSE_PARENS:
            tok = Token(self.char, CLOSE_PARENS)
            self.next_char()
        elif self.char == OPEN_BRACKET:
            tok = Token(self.char, OPEN_BRACKET)
            self.next_char()
        elif self.char == CLOSE_BRACKET:
            tok = Token(self.char, CLOSE_BRACKET)
            self.next_char()
        elif self.char == NEWLINE:
            tok = Token(NEWLINE, NEWLINE)
            self.next_char()
        elif self.char == EOF:
            return Token(EOF, EOF)
        else:
            self.error('Unrecognized character')
        self.skip_whitespaces()
        return tok

