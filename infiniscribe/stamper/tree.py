# coding: utf-8

'''
===============================================================================
Infiniscribe - The Infinite Automaton Scriber of Nimus Ages

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/hacktoon/infiniscribe
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
===============================================================================
'''

import os
from datetime import datetime
import operator

from .exceptions import BreakStatement, FunctionReturn, FileNotFoundError


class Node:
    def __init__(self, value='', token=None):
        self.value = value
        self.token = token
        self.children = []

    def lookup_context(self, context, name):
        name = name.split('.')
        ref = context.get(name[0], '')
        for part in name[1:]:
            if part not in ref:
                return ''
            ref = ref[part]
        return ref

    def add_child(self, child):
        if isinstance(child, list):
            self.children.extend(child)
        else:
            self.children.append(child)

    def build_output(self, output_list):
        return ''.join(output_list)

    def render(self, context):
        output = []
        for child in self.children:
            try:
                child_output = str(child.render(context))
            except BreakStatement as break_stmt:
                partial_output = self.build_output(output)
                break_stmt.partial_output = partial_output
                raise break_stmt
            output.append(child_output)
        return self.build_output(output)

    def load_file(self, filename, path=''):
        if not isinstance(filename, str):
            self.error(RuntimeError, 'String expected')
        filename = os.path.join(path, filename)
        try:
            with open(filename, 'r') as fp:
                file_content = fp.read()
        except IOError:
            msg = 'File {!r} not found'.format(filename)
            self.error(FileNotFoundError, msg)
        return file_content

    def error(self, exception_class, msg):
        raise exception_class(msg, self.token, self.parser)

    def __str__(self):
        return '{} - [{}]\n'.format(type(self), str(self.value))


class Root(Node):
    def render(self, context):
        try:
            output = super().render(context)
        except (RuntimeError, FileNotFoundError) as err:
            err.parser.error(err, err.token)
        except BreakStatement as break_stmt:
            err.parser.error('Invalid break statement', break_stmt.token)
        except FunctionReturn as func_return:
            err.parser.error('Invalid return statement', func_return.token)
        return output


class Text(Node):
    def render(self, _):
        return self.value


class Variable(Node):
    def render(self, context):
        return self.lookup_context(context, self.value)


class Number(Node):
    def render(self, _):
        return int(self.value)


class String(Node):
    def render(self, _):
        return self.value


class Boolean(Node):
    def render(self, _):
        vmap = {'true': True, 'false': False}
        return vmap[self.value]


class UnaryMinus(Node):
    def render(self, context):
        output = super().render(context)
        return operator.neg(output)


class Operation(Node):
    def render(self, context):
        output = self.children[0].render(context)
        # need to calculate with first child because of the NOT
        try:
            if len(self.children) > 1:
                for child in self.children[1:]:
                    output = self.value(output, child.render(context))
            else:
                output = self.value(output)
        except ZeroDivisionError:
            self.error(RuntimeError, 'Division by zero')
        except TypeError:
            self.error(RuntimeError, 'Wrong types in operation')
        return output


class Condition(Node):
    def __init__(self, value, token):
        super().__init__(value, token)
        self.true_block = None
        self.false_block = None

    def render(self, context):
        if self.value.render(context):
            self.children = self.true_block
        elif self.false_block:  # just check if there's an ELSE clause
            self.children = self.false_block
        else:
            self.children = []
        return super().render(context)


class WhileLoop(Node):
    def render(self, context):
        output = []
        while self.value.render(context):
            try:
                text = super().render(context)
            except BreakStatement as break_stmt:
                output.append(break_stmt.partial_output)
                break
            output.append(text)
        return self.build_output(output)


class ListNode(Node):
    def __init__(self, iter_name, collection_name, token, reverse=False, limit=None):
        super().__init__('list {} as {}'.format(collection_name, iter_name), token)
        self.iter_name = iter_name
        self.collection_name = collection_name
        self.reverse = reverse
        self.limit = limit

    def update_iteration_counters(self, context, collection, index):
        item = context[self.iter_name]
        counter = item['loop'] = {}
        counter['first'] = True if index == 0 else False
        counter['last'] = True if index == len(collection) - 1 else False
        counter['index'] = index
        counter['length'] = len(collection)

    def render(self, context):
        output = []
        collection = context.get(self.collection_name)
        loop_context = context.copy()
        if self.reverse:
            collection = list(collection)
            collection.reverse()
        for index, item in enumerate(collection):
            if self.limit and index > self.limit - 1:
                break
            loop_context[self.iter_name] = item
            self.update_iteration_counters(loop_context, collection, index)
            try:
                text = super().render(loop_context)
            except BreakStatement as break_stmt:
                output.append(break_stmt.partial_output)
                break
            output.append(text)
        return self.build_output(output)


class FunctionNode(Node):
    def __init__(self, value, params, token):
        super().__init__(value, token)
        self.params = params
        self.context = {}

    def call(self, args):
        received, expected = len(args), len(self.params)
        if expected > received:
            msg = 'Expected {} params, received {}'.format(expected, received)
            self.error(RuntimeError, msg)
        scoped_context = dict(zip(self.params, args))
        self.context.update(scoped_context)
        try:
            output = super().render(self.context)
        except FunctionReturn as func_return:
            return func_return.return_value
        return output

    def render(self, context):
        context[self.value] = self
        self.context = context.copy()
        return ''


class FunctionCall(Node):
    def __init__(self, value, args, token):
        super().__init__(value, token)
        self.args = args

    def render(self, context):
        func = self.lookup_context(context, self.value)
        if not func:
            msg = 'Function {!r} not defined'.format(self.value)
            self.error(RuntimeError, msg)
        args = [arg.render(context) for arg in self.args]
        return func.call(args)


class ReturnCommand(Node):
    def render(self, context):
        return_value = self.value.render(context)
        raise FunctionReturn(self.token, return_value)


class BreakCommand(Node):
    def render(self, _):
        raise BreakStatement(token=self.token)


class PrintCommand(Node):
    def __init__(self, value, token, tag_filter=None):
        super().__init__(value, token)
        self.tag_filter = tag_filter

    def render(self, context):
        value = self.value.render(context)
        if isinstance(value, datetime):
            if self.tag_filter:
                value = value.strftime(self.tag_filter)
            else:
                value = value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value)


class IncludeCommand(Node):
    def render(self, context):
        path = self.parser.include_path
        filename = self.value.render(context)
        return self.load_file(filename, path)


class ParseCommand(Node):
    def __init__(self, value, parser, token):
        super().__init__(value, token)
        self.parser_cls = parser

    def render(self, context):
        path = self.parser.include_path
        filename = self.value.render(context)
        file_content = self.load_file(filename, path)
        try:
            p = self.parser_cls(file_content, filename=filename)
            subtree = p.parse()
        except RuntimeError:
            msg = '{} is including itself.'.format(filename)
            self.error(RuntimeError, msg)
        return subtree.render(context)


class Assignment(Node):
    def __init__(self, value, token):
        super().__init__(value, token)
        self.rvalue = None

    def render(self, context):
        value = self.rvalue.render(context)
        context[self.value] = value
        return ''

