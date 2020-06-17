# coding: utf-8

'''
===============================================================================
Sitegen

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/sitegen
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

import sys
import operator
import re

NUMBER = 'number'
STRING = 'string'
IDENTIFIER = 'identifier'
KEYWORD = 'keyword'
TEXT = 'text'
SYMBOL = 'symbol'
WHITESPACE = 'whitespace'

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
PIPE = '|'

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
LIMIT = 'limit'
BREAK = 'break'

BOOLEAN_VALUES = ['true', 'false']

OPEN_CMD = '{%'
CLOSE_CMD = '%}'
OPEN_VAR = '{{'
CLOSE_VAR = '}}'
OPEN_COMMENT = '{#'
CLOSE_COMMENT = '#}'

TAG_VAR_OPEN = 'open_var'
TAG_VAR_CLOSE = 'close_var'
TAG_CMD_OPEN = 'open_cmd'
TAG_CMD_CLOSE = 'close_cmd'
TAG_COMMENT_OPEN = 'open_comment'
TAG_COMMENT_CLOSE = 'close_comment'

TAG_MAP = {
    TAG_VAR_OPEN: OPEN_VAR,
    TAG_VAR_CLOSE: CLOSE_VAR,
    TAG_CMD_OPEN: OPEN_CMD,
    TAG_CMD_CLOSE: CLOSE_CMD,
    TAG_COMMENT_OPEN: OPEN_COMMENT,
    TAG_COMMENT_CLOSE: CLOSE_COMMENT
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

    # using \b in keywords avoids matching "use" in "used"
    KEYWORDS = r'\b|\b'.join([IF, ELSE, WHILE, AS,
        FUNCTION, RETURN, PRINT, INCLUDE, BOOL_NOT,
        BOOL_AND, BOOL_OR, PARSE, END, LIST, REVLIST,
        USE, REGION, LIMIT, BREAK])

    TAGS = []
    for key, tag in TAG_MAP.items():
        TAGS.append('(?P<{}>{})'.format(key, re.escape(tag)))

    # organize by matching priority
    regex = '|'.join([
        '|'.join(TAGS),
        r'(?P<{}>\b{}\b)'.format(KEYWORD, KEYWORDS),
        r'(?P<{}>\b[a-zA-Z_]\w*(\.[a-zA-Z_]\w*)*\b)'.format(IDENTIFIER),
        r'(?P<{}>\".*?\"|\'.*?\')'.format(STRING),
        r'(?P<{}>[-+]?[0-9]+)'.format(NUMBER),
        r'(?P<{}>{})'.format(SYMBOL, SYMBOLS),
        r'(?P<{}>\s+)'.format(WHITESPACE),
        r'(?P<unknow>.)'
    ])
    return re.compile(regex, re.DOTALL)

def build_tag_regex():
    base = '(?P<{}>{}.*?{})'
    e = re.escape
    tag_re = '|'.join([
        base.format(TAG_VAR_OPEN, e(OPEN_VAR), e(CLOSE_VAR)),
        base.format(TAG_CMD_OPEN, e(OPEN_CMD), e(CLOSE_CMD)),
        base.format(TAG_COMMENT_OPEN, e(OPEN_COMMENT), e(CLOSE_COMMENT))
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
        return '{} [{}] - {}'.format(self.type, self.value, self.column)


class Lexer:
    def __init__(self):
        self.tokens = []

    def make_token(self, type, value, index_in_tpl):
        self.tokens.append(Token(type, value, index_in_tpl))

    def extract_tokens(self, text, tag_matched):
        offset = tag_matched.start()
        for match in TOKEN_REGEX.finditer(text):
            # ignore these tokens, emit only the VAR type
            if match.lastgroup in (WHITESPACE, TAG_CMD_OPEN, TAG_CMD_CLOSE):
                continue
            value = text[match.start(): match.end()]
            if match.lastgroup == STRING:
                value = value[1:-1]  # remove string quotes
            index = match.start() + offset
            self.make_token(match.lastgroup, value, index)

    def tokenize(self, template):
        index = 0
        for match in TAG_REGEX.finditer(template):
            start = match.start()
            end = match.end()
            if template[index:start]:
                self.make_token(TEXT, template[index:start], index)
            if match.lastgroup != TAG_COMMENT_OPEN:
                self.extract_tokens(template[start: end], match)
            index = end
        if template[index:]:
            self.make_token(TEXT, template[index:], index)
        return self.tokens
