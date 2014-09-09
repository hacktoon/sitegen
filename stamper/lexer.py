import sys
import re
import operator

NEWLINE = '\n'
STRING_DELIMITERS = ['"', "'"]
NUMBER = 'Number'
STRING = 'String'
IDENTIFIER = 'Identifier'
KEYWORD = 'Keyword'
TEXT = 'Text'
SYMBOL = 'Symbol'

OPEN_CMD = '{%'
CLOSE_CMD = '%}'
OPEN_VAR = '{{'
CLOSE_VAR = '}}'
OPEN_COMMENT = '{#'
CLOSE_COMMENT = '#}'

OPEN_PARENS = '('
CLOSE_PARENS = ')'
COLON = ':'
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
VALID_SYMBOLS = (EQUAL, DIFF, LE, GE, LT,
    GT, PLUS, MINUS, MUL, DIV, MOD, COMMA,
    ASSIGN, COLON, OPEN_PARENS,
    CLOSE_PARENS, DOT)
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
USE = 'use'
REGION = 'region'
KEYWORDS = (IF, ELSE, WHILE, AS,
    FUNCTION, RETURN, PRINT, INCLUDE,
    PARSE, END, LIST, REVLIST, USE, REGION)

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
    DIFF: operator.ne,
    BOOL_AND: lambda x,y: x and y,
    BOOL_OR: lambda x,y: x or y,
    BOOL_NOT: lambda x: not x
}

TAG_REGEX = re.compile(r'(?P<var>{{.*?}})|(?P<cmd>{%.*?%})|(?P<comment>{#.*?#})')

class Token():
    def __init__(self, val, type, line, column):
        self.value = val
        self.type = type
        self.line = line
        self.column = column

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
    def __init__(self, template):
        self.index = 0
        self.template = template
        self.line = 1
        self.column = 1

    def update_count(substr):
        for char in substr:
            self.index += 1
            if char == '\n':
                self.line += 1
                self.column = 1
                continue
            self.column += 1
    
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

    def get_symbol(self):
        symbol = self.char + self.template[self.index]
        if symbol in VALID_SYMBOLS:
            self.next_char()
            self.next_char()
        elif self.char in VALID_SYMBOLS:
            symbol = self.char
            self.next_char()
        else:
            self.error('Invalid symbol {!r}'.format(symbol))
        return Token(symbol, SYMBOL)

    def strip_tags(self, tag):
        re.sub()

    def tokenize(self, tag):
        self.skip_whitespaces()

        if self.char == EOF:
            tok = Token(EOF, EOF)
        elif self.char.isdigit():
            tok = self.get_number()
        elif self.char.isalpha():
            tok = self.get_name()
        elif self.issymbol(self.char):
            tok = self.get_symbol()
        elif self.char in STRING_DELIMITERS:
            tok = self.get_string(self.char)
        else:
            self.error('Unrecognized character {!r}'.format(self.char))
        return tok

    def make_token(self, value, type):
        self.update_count(value)
        return Token(value, type, self.line, self.column)

    def get_token(self):
        match_column = 0
        template = self.template
        for match in TAG_REGEX.finditer(template):
            start, end = match.start(), match.end()
            matches = match.groupdict()
            tag_type = [key for key,val in matches.items() if val][0]
            text = template[match_column:start]
            if text:
                yield self.make_token(text, TEXT)
            for token in self.tokenize(matches[tag_type], tag_type)
                yield token
            match_column = end

        # produces a token with the rest of the text
        text = template[match_column:]
        if text:
            yield self.make_token(text, TEXT)

        
