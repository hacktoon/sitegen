import sys
import operator
import re

NEWLINE = '\n'

NUMBER = 'number'
STRING = 'string'
IDENTIFIER = 'identifier'
KEYWORD = 'keyword'
TEXT = 'text'
SYMBOL = 'symbol'
WHITESPACE = 'whitespace'

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

ID_OPEN_VAR = 'open_var'
ID_CLOSE_VAR = 'close_var'
ID_COMMAND_OPEN = 'open_cmd'
ID_COMMAND_CLOSE = 'close_cmd'
ID_COMMENT_OPEN = 'open_comment'
ID_COMMENT_CLOSE = 'close_comment'

TAG_MAP = {
    ID_OPEN_VAR: OPEN_VAR,
    ID_CLOSE_VAR: CLOSE_VAR,
    ID_COMMAND_OPEN: OPEN_CMD,
    ID_COMMAND_CLOSE: CLOSE_CMD,
    ID_COMMENT_OPEN: OPEN_COMMENT,
    ID_COMMENT_CLOSE: CLOSE_COMMENT
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

def build_token_regex():
    # double char symbols must come first
    SYMBOLS = (EQUAL, DIFF, LE, GE, LT, GT, PLUS,
        MINUS, MUL, DIV, MOD, COMMA, ASSIGN, COLON,
        OPEN_PARENS, CLOSE_PARENS, DOT)
    SYMBOLS = '|'.join([re.escape(x) for x in SYMBOLS])

    KEYWORDS = r'\b|\b'.join([IF, ELSE, WHILE, AS,
        FUNCTION, RETURN, PRINT, INCLUDE, BOOL_NOT,
        BOOL_AND, BOOL_OR, PARSE, END, LIST, REVLIST,
        USE, REGION])

    TAGS = []
    for key, tag in TAG_MAP.items():
        TAGS.append('(?P<{}>{})'.format(re.escape(key), re.escape(tag)))

    # organize by matching priority
    # using \b in keywords avoids matching "use" in "used"
    regex = '|'.join([
        '|'.join(TAGS),
        r'(?P<{}>\b{}\b)'.format(KEYWORD, KEYWORDS),
        r'(?P<{}>\b[a-zA-Z_]\w*(\.[a-zA-Z_]\w*)?\b)'.format(IDENTIFIER),
        r'(?P<{}>\".*?\"|\'.*?\')'.format(STRING),
        r'(?P<{}>[-+]?[0-9]+)'.format(NUMBER),
        r'(?P<{}>{})'.format(SYMBOL, SYMBOLS),
        r'(?P<{}>\s+)'.format(WHITESPACE),
        r'(?P<unknow>.)'
    ])
    return re.compile(regex, re.DOTALL)

def build_tag_regex():
    base = '({}.*?{})'
    tag_re = '|'.join([
        base.format(OPEN_VAR, CLOSE_VAR),
        base.format(OPEN_CMD, CLOSE_CMD),
        base.format(OPEN_COMMENT, CLOSE_COMMENT),
    ])
    return re.compile(tag_re, re.DOTALL)

TAG_REGEX = build_tag_regex()
TOKEN_REGEX = build_token_regex()


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
        self.lines = template.split('\n')
        self.tokens = []
        self.linemap = {}
        self.show_line_error(68)
        print(template[69:71])

    def show_line_error(self, index):
        start = 0
        end = 0
        for line in self.lines:
            end = start + len(line) - 1
            if start <= index <= end:
                print('Error at line {}!'.format())
                print(line)
                mark = list(' ' * len(line))
                mark[index - start] = '^'
                print(''.join(mark))
                break
            start += len(line)

    def error(self, msg):
        line = 0
        column = 0
        sys.exit('Error: {} at line {}, column {}'.format(msg, line, column))
    
    def make_token(self, type, value, index_in_tpl):
        return Token(type, value, index_in_tpl)

    def extract_tokens(self, text, tag_matched):
        offset = tag_matched.start()
        for match in TOKEN_REGEX.finditer(text):
            if match.lastgroup == WHITESPACE:
                continue
            value = text[match.start(): match.end()]
            # offset value = start position of the entire tag
            index = match.start() + offset - 1
            self.tokens.append(Token(match.lastgroup, value, index))

    def tokeniter(self):
        index = 0
        text = self.template
        for match in TAG_REGEX.finditer(text):
            start = match.start()
            end = match.end()
            if text[index:start]:
                self.tokens.append(Token(TEXT, text[index:start], index))
            self.extract_tokens(text[start: end], match)
            index = end
        if text[index:]:
            self.tokens.append(Token(TEXT, text[index:], index))
        return self.tokens

        
