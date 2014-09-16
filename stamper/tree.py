import os
import sys

from . import exceptions

def load_file(self, filename):
    if not isinstance(filename, str):
        raise exceptions.RuntimeError('String expected')

    try:
        fp = open(filename, 'r')
    except:
        msg = 'File {!r} not found'.format(filename)
        raise exceptions.FileNotFoundError(msg)
    file_content = fp.read()
    fp.close()
    return file_content


class Node:
    def __init__(self, value='', token=None):
        self.value = value
        self.token = token
        self.children = []

    def lookup_context(self, context, name):
        name = name.split('.')
        ref = context.get(name[0])
        for part in name[1:]:
            try:
                ref = ref.get(part)
            except AttributeError as error:
                return
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
                rendered = str(child.render(context))
            except exceptions.RuntimeError as error:
                sys.exit('Error: {} {}'.format(error, self.token.column))
            output.append(rendered)
            if isinstance(child, ReturnCommand):
                return self.build_output(output)
        return self.build_output(output)

    def __str__(self):
        return '{} - [{}]\n'.format(type(self), str(self.value))


class Text(Node):
    def render(self, _):
        return self.value


class Variable(Node):
    def render(self, context):
        value = self.lookup_context(context, self.value)
        return value


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
            raise exceptions.RuntimeError('Division by zero')
        except TypeError:
            raise exceptions.RuntimeError('Wrong types in operation')
        return output


class Condition(Node):
    def __init__(self, value, token):
        super().__init__(value, token)
        self.true_block = None
        self.false_block = None

    def render(self, context):
        if self.value.render(context):
            self.children = self.true_block
        elif self.false_block: # just check if there's an ELSE clause
            self.children = self.false_block
        else:
            self.children = []
        return super().render(context)


class WhileLoop(Node):
    def render(self, context):
        output = []
        while self.value.render(context):
            text = super().render(context)
            output.append(text)
        return self.build_output(output)


class List(Node):
    def __init__(self, iter_name, collection_name, token, reverse=False):
        super().__init__('List', token)
        self.iter_name = iter_name
        self.collection_name = collection_name
        self.reverse = reverse

    def update_iteration_counters(self, context, collection, index):
        context[self.iter_name].update({
            'first': True if index == 0 else False,
            'last': True if index == len(collection) - 1 else False,
            'index': index
        })

    def render(self, context):
        output = []
        collection = context.get(self.collection_name)
        if self.reverse:
            collection = list(collection)
            collection.reverse()
        for index, item in enumerate(collection):
            list_context = context.copy()
            list_context[self.iter_name] = item
            self.update_iteration_counters(list_context, collection, index)
            text = super().render(list_context)
            output.append(text)
        return self.build_output(output)


class Function(Node):
    def __init__(self, value, params, token):
        super().__init__(value, token)
        self.params = params
        self.context = {}

    def call(self, args):
        received = len(args)
        expected = len(self.params)
        if expected > received:
            msg = 'Expected {} params, received {}'.format(expected, received)
            raise exceptions.RuntimeError(msg)
        scope_context = dict(zip(self.params, args))
        self.context.update(scope_context)
        return super().render(self.context)

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
            raise exceptions.RuntimeError('Function {!r} not defined'
                .format(self.value))
        args = [arg.render(context) for arg in self.args]
        return func.call(args)


class ReturnCommand(Node):
    def render(self, context):
        return self.value.render(context)


class PrintCommand(Node):
    def render(self, context):
        return str(self.value.render(context))


class IncludeCommand(Node):
    def render(self, context):
        filename = self.value.render(context)
        return load_file(filename)


class ParseCommand(Node):
    def __init__(self, value, parser, token):
        super().__init__(value, token)
        self.parser = parser

    def render(self, context):
        filename = self.value.render(context)
        file_content = load_file(filename)
        try:
            subtree = self.parser(file_content).parse()
        except RuntimeError:
            sys.exit('{} is including itself.'.format(filename))
        return subtree.render(context)


class Assignment(Node):
    def __init__(self, value, token):
        super().__init__(value, token)
        self.rvalue = None

    def render(self, context):
        value = self.rvalue.render(context)
        context[self.value] = value
        return ''