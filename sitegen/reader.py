# -*- encoding: UTF-8 -*-

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
from .exceptions import PageValueError

NEWLINE = '\n'

TOK_NAME = 'name'
TOK_TEXT = 'content'
TOK_ESCAPE = '\\'
TOK_EOF = '\0'
TOK_ASSIGN = '='
TOK_COMMA = ','
TOK_OPENLIST = '['
TOK_CLOSELIST = ']'
TOK_OPENGROUP = '{'
TOK_CLOSEGROUP = '}'

KEYCHARS = ''.join([
        NEWLINE,
        TOK_ASSIGN,
        TOK_COMMA,
        TOK_OPENLIST,
        TOK_CLOSELIST,
        TOK_OPENGROUP,
        TOK_CLOSEGROUP
])

def _create_env(text):
        data = {}
        return {
                'index': 0,
                'text': text,
                'tokens': [],
                'current_token': None,
                'data': data,
                'stack': [data]
        }

def _create_token(type, value, line=1, column=0):
        return {
                'type': type,
                'value': value,
                'line': line,
                'column': column
        }

def _tokenize(text):
        line = 1
        column = 0
        cache = []
        tokens = []
        inlist = False
        text = text.strip()
        escape = False
        for index, char in enumerate(text):
                if char == TOK_ESCAPE:
                    escape = True
                    continue
                if char in KEYCHARS and escape:
                    cache.append(char)
                    column += 1
                    escape = False
                    continue
                if char not in KEYCHARS or not inlist and char == TOK_COMMA:
                        cache.append(char)
                        column += 1
                        continue
                name = ''.join(cache).strip()
                inlist = {
                        TOK_OPENLIST: True,
                        TOK_CLOSELIST: False
                }.get(char, inlist)
                if name == TOK_TEXT:
                        token = _create_token(TOK_TEXT, text[index:].strip(), line, column)
                        tokens.append(token)
                        return tokens
                if name:
                        tokens.append(_create_token(TOK_NAME, name, line, column))
                if char == NEWLINE:
                        line += 1
                        column = 0
                else:
                        column += 1
                        tokens.append(_create_token(char, char, line, column))
                cache = []

        # remaining chars
        name = ''.join(cache).strip()
        if name:
                tokens.append(_create_token(TOK_NAME, name, line, column))
        return tokens

def _error(env, msg):
        token = env['current_token']
        raise PageValueError('{} at line {}, column {}'.format(
                msg, token['line'], token['column']))

def _next_token(env):
        env['index'] += 1
        try:
                next = env['tokens'][env['index']]
        except IndexError:
                next = _create_token(TOK_EOF, TOK_EOF)
        env['current_token'] = next
        return next

def _consume(env, expected):
        token = env['current_token']
        if token['type'] == TOK_EOF:
                return
        if token['type'] != expected:
                _error(env, 'Expected a {!r}'.format(expected))
        _next_token(env)

def _parse_group(env):
        rules = {}
        env['stack'].append(rules)
        while env['current_token']['type'] not in (TOK_CLOSEGROUP, TOK_EOF):
                _parse_rule(env)
        _consume(env, TOK_CLOSEGROUP)
        env['stack'].pop()
        return rules

def _parse_list(env):
        names = []
        while True:
                token = env['current_token']
                if token['type'] == TOK_CLOSELIST:
                        _next_token(env)
                        break
                if token['type'] == TOK_NAME:
                        names.append(token['value'])
                        _next_token(env)
                else:
                        _error(env, 'Expected a name, got {!r}'.format(token['value']))
                token = env['current_token']
                if token['type'] == TOK_COMMA:
                        token = _next_token(env)
                        continue
                elif token['type'] == TOK_CLOSELIST:
                        _next_token(env)
                        break
                else:
                        _error(env, 'Invalid syntax')
        return names

def _parse_value(env):
        token = env['current_token']
        if token['type'] == TOK_NAME:
                value = token['value']
                _next_token(env)
        elif token['type'] == TOK_OPENLIST:
                _next_token(env)
                value = _parse_list(env)
        elif token['type'] == TOK_OPENGROUP:
                _next_token(env)
                value = _parse_group(env)
        else:
                _error(env, 'Invalid value format')
        return value

def _parse_rule(env):
        token = env['current_token']
        if token['type'] not in (TOK_NAME, TOK_TEXT):
                _error(env, 'Expected a name, got {!r}'.format(token['value']))
        name = token['value']
        if token['type'] == TOK_TEXT:
                if len(env['stack']) > 1:
                        _error(env, 'Wrong syntax')
                env['data'][TOK_TEXT] = token['value']
                _next_token(env)
                return
        token = _next_token(env)
        if token['type'] == TOK_ASSIGN:
                _next_token(env)
                value = _parse_value(env)
                env['stack'][-1][name] = value
        else:
                _error(env, 'Invalid syntax')

def _parse_ruleset(env):
        while env['current_token']['type'] not in (TOK_EOF, TOK_CLOSEGROUP):
                _parse_rule(env)
        return env['data']

def repr_token(t):
        tpl = '{}\t[{}]\t\t({},{})'
        return tpl.format(t['type'], t['value'], t['line'], t['column'])

def parse(text):
        if not len(text.strip()):
                return {}
        env = _create_env(text)
        tokens = _tokenize(text)
        env['tokens'] = tokens
        env['current_token'] = tokens[0]
        return _parse_ruleset(env)
