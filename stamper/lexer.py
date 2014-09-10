import sys
import operator
import re

NEWLINE = '\n'

NUMBER = 'number'
STRING = 'string'
IDENTIFIER = 'identifier'
KEYWORD = 'keyword'
TEXT_TYPE = 'text'
SYMBOL = 'symbol'

OPEN_CMD = '{%'
CLOSE_CMD = '%}'
OPEN_VAR = '{{'
CLOSE_VAR = '}}'
OPEN_COMMENT = '{#'
CLOSE_COMMENT = '#}'

#symbols
OPEN_PARENS = '('
CLOSE_PARENS = ')'
EQUAL = '=='
DIFF = '!='
LE = '<='
GE = '>='
LT = '<'
GT = '>'
ASSIGN = '='
PLUS = '+'
COLON = ':'
MINUS = '-'
MUL = '*'
DIV = '/'
MOD = '%'
COMMA = ','
DOT = '.'

# keywords
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

BOOLEAN_VALUES = ['true', 'false']

TAG_MAP = {
    'variable': (OPEN_VAR, CLOSE_VAR),
    'command': (OPEN_CMD, CLOSE_CMD),
    'comment': (OPEN_COMMENT, CLOSE_COMMENT)
}

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


COMPOUND_SYMBOLS = (EQUAL, DIFF, LE, GE)
SINGLE_SYMBOLS = (LT, GT, PLUS, MINUS, 
    MUL, DIV, MOD, COMMA, ASSIGN, COLON,
    OPEN_PARENS, CLOSE_PARENS, DOT)
SYMBOLS = '|'.join([re.escape(x) for x in COMPOUND_SYMBOLS+SINGLE_SYMBOLS])

KEYWORDS = '|'.join([IF, ELSE, WHILE, AS,
    FUNCTION, RETURN, PRINT, INCLUDE,
    PARSE, END, LIST, REVLIST, USE, REGION])

# organize by matching priority
RE_TOKENS = '|'.join([
    r'(?P<keyword>'+KEYWORDS+')',
    r'(?P<identifier>[a-zA-Z_][a-zA-Z0-9_]*(\.[_a-zA-Z_][_a-zA-Z0-9_]*)?)',
    r'(?P<string>\".*?\"|\'.*?\')',
    r'(?P<number>[-+]?[0-9]+)',
    r'(?P<symbol>'+SYMBOLS+')',
    r'(?P<whitespace>\s+)',
    r'(?P<unknow>.)'
])

def build_tag_regex():
    exp = []
    for name, delimiter in TAG_MAP.items():
        topen = re.escape(delimiter[0])
        tclose = re.escape(delimiter[1])
        tag_re = '(?P<{}>{}.*?{})'.format(name, topen, tclose)
        exp.append(tag_re)
    return re.compile('|'.join(exp), re.DOTALL)

TAG_REGEX = build_tag_regex()
tokens_regex = re.compile(RE_TOKENS, re.DOTALL)

class Token():
    def __init__(self, type, value, column):
        self.value = value
        self.type = type
        self.column = column

    def check_symbol(self, *values):
        return self.value in values
    
    def is_addop(self):
        return self.check_symbol(PLUS, MINUS)

    def is_mulop(self):
        return self.check_symbol(MUL, DIV, MOD)

    def is_equop(self):
        return self.check_symbol(EQUAL, DIFF)

    def is_relop(self):
        return self.check_symbol(LT, LE, GE, GT)

    def __str__(self):
        return '{} [{}] - {}'.format(self.type, self.value.strip(), self.column)


class Lexer:
    def __init__(self, template):
        self.template = template
        self.tokens = []

    def error(self, msg):
        line = 0
        column = self.column
        sys.exit('Error: {} at line {}, column {}'.format(msg, line, column))

    def strip_tags(self, text, tag_type):
        pattern = '|'.join([re.escape(x) for x in TAG_MAP[tag_type]])
        return re.sub(pattern, '', text)

    def extract_tokens(self, text, tag_matched):
        start = tag_matched.start()
        tag_type = tag_matched.lastgroup
        text = self.strip_tags(text, tag_type)
        for match in tokens_regex.finditer(text):
            if match.lastgroup == 'whitespace':
                continue
            column = match.start()+start+len(TAG_MAP[tag_type][0])
            value = text[match.start(): match.end()]
            return Token(match.lastgroup, value, column)

    def tokeniter(self):
        column = 0
        text = self.template
        for match in TAG_REGEX.finditer(text):
            start = match.start()
            end = match.end()
            if text[column:start]:
                self.tokens.append(Token(TEXT_TYPE, text[column:start], column))
            self.tokens.append(self.extract_tokens(text[start: end], match))
            column = end
        if text[column:]:
            self.tokens.append(Token(TEXT_TYPE, text[column:], column))
        return self.tokens

        
