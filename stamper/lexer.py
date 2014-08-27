import sys
import operator

EOF = '\0'
NEWLINE = '\n'
STRING_DELIMITERS = ['"', "'"]
NUMBER = 'Number'
STRING = 'String'
IDENTIFIER = 'Identifier'
KEYWORD = 'Keyword'
TEXT = 'Text'
SYMBOL = 'Symbol'
OPEN_PARENS = '('
CLOSE_PARENS = ')'
COLON = ':'
OPEN_TAG = '{%'
CLOSE_TAG = '%}'
ASSIGN = '='
EQUAL = '=='
DIFF = '!='
LE = '<='
GE = '>='
LT = '<'
GT = '>'
PLUS = '+'
MINUS = '-'
MUL = '*'
DIV = '/'
MOD = '%'
COMMA = ','
DOT = '.'
SEMICOLON = ';'
VALID_SYMBOLS = (EQUAL, DIFF, LE, GE, LT,
    GT, PLUS, MINUS, MUL, DIV, MOD, COMMA,
    SEMICOLON, ASSIGN, COLON, OPEN_PARENS,
    CLOSE_PARENS, CLOSE_TAG, DOT)
SYMBOLS = set(''.join(VALID_SYMBOLS))

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
INCLUDE = 'include'
PARSE = 'parse'
END = 'end'
LIST = 'list'
REVLIST = 'rlist'
AS = 'as'
KEYWORDS = (IF, ELSE, WHILE, BOOL_OR, AS,
    BOOL_AND, BOOL_NOT, FUNCTION, RETURN,
    PRINT, INCLUDE, PARSE, END, LIST, REVLIST)

OPMAP = {
    MUL: operator.mul,
    DIV: operator.floordiv,
    MOD: operator.mod,
    PLUS: operator.add,
    MINUS: operator.sub,
    GT: operator.gt,
    GE: operator.ge,
    LT: operator.lt,
    LE: operator.le,
    EQUAL: operator.eq,
    DIFF: operator.ne
}


class Token():
    def __init__(self, val, type):
        self.value = val
        self.type = type

    def check_symbol(self, *values):
        return self.type == SYMBOL and self.value in values
    
    def is_addop(self):
        return self.check_symbol(PLUS, MINUS)

    def is_mulop(self):
        return self.check_symbol(MUL, DIV, MOD)

    def is_equop(self):
        return self.check_symbol(EQUAL, DIFF)

    def is_relop(self):
        return self.check_symbol(LT, LE, GE, GT)

    def __str__(self):
        return '{} [{}]'.format(self.type, self.value)


class Lexer():
    def __init__(self, code):
        self.index = 0
        self.code = code
        self.len = len(code)
        self.line = 1
        self.column = 1
        self.char = self.get_char()
        self.char_buffer = ''
        self.text_mode = True
    
    def get_char(self):
        if self.index >= self.len:
            return EOF
        char = self.code[self.index]
        self.column += 1
        self.index += 1
        if char == NEWLINE:
            self.line += 1
            self.column = 1
        return char

    def issymbol(self, c):
        return c in SYMBOLS

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
        while self.char.isalnum() or self.char == '_':
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

    def peek(self):
        return self.code[self.index]

    def get_symbol(self):
        symbol = self.char + self.peek()
        if symbol in VALID_SYMBOLS:
            self.next_char()
            self.next_char()
        elif self.char in VALID_SYMBOLS:
            symbol = self.char
            self.next_char()
        else:
            self.error('Invalid symbol {!r}'.format(symbol))
        return Token(symbol, SYMBOL)

    def get_text(self):
        while not self.char_buffer.endswith(OPEN_TAG) and self.char != EOF:
            self.char_buffer += self.char
            self.next_char()
        text = self.char_buffer.replace(OPEN_TAG, '')
        self.text_mode = False
        self.char_buffer = ''
        return Token(text, TEXT)

    def get_token(self):
        tok = None

        if self.text_mode:
            return self.get_text()
        self.skip_whitespaces()

        if self.char == EOF:
            tok = Token(EOF, EOF)
        elif self.char.isdigit():
            tok = self.get_number()
        elif self.char.isalpha():
            tok = self.get_name()
        elif self.issymbol(self.char):
            tok = self.get_symbol()
            if tok.value == CLOSE_TAG:
                self.text_mode = True
                tok = self.get_token()
        elif self.char in STRING_DELIMITERS:
            tok = self.get_string(self.char)
        else:
            self.error('Unrecognized character {!r}'.format(self.char))
        return tok
