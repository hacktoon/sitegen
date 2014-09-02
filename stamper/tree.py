import os

def load_file(self, filename):
    if not isinstance(filename, str):
        raise Exception('String expected')
    try:
        fp = open(filename, 'r')
    except:
        raise Exception('File not found')
    file_path = os.path.realpath(filename)
    file_content = fp.read()
    fp.close()
    return file_content

class Node:
    def __init__(self, value=''):
        self.value = value
        self.children = []

    def lookup_context(self, context, name):
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
            output.append(str(child.render(context)))
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
        if not value:
            raise Exception('Variable {!r} not defined'
                .format('.'.join(self.value)))
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
        for child in self.children[1:]:
            output = self.value(output, child.render(context))
        return output


class Condition(Node):
    def __init__(self, value):
        super().__init__(value)
        self.true_block = None
        self.false_block = None

    def render(self, context):
        if self.value.render(context):
            self.children = self.true_block
        elif self.false_block: # just check if there's an ELSE clause
            self.children = self.false_block
        return super().render(context)


class WhileLoop(Node):
    def render(self, context):
        output = []
        while self.value.render(context):
            text = super().render(context)
            output.append(text)
        return self.build_output(output)


class List(Node):
    def __init__(self, iter_name, collection, reverse=False):
        super().__init__('List')
        self.iter_name = iter_name
        self.collection = collection
        self.reverse = reverse

    def render(self, context):
        output = []
        collection = context.get(self.collection)
        if self.reverse:
            collection = list(collection)
            collection.reverse()
        # TODO - iterable variables
        for i, item in enumerate(collection):
            for_context = context.copy()
            for_context[self.iter_name] = item
            text = super().render(for_context)
            output.append(text)
        return self.build_output(output)


class Function(Node):
    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.context = {}

    def call(self, args):
        received = len(args)
        expected = len(self.params)
        if expected > received:
            raise Exception('Expected {} params, '
                'received {}'.format(expected, received))
        scope_context = dict(zip(self.params, args))
        self.context.update(scope_context)
        return super().render(self.context)

    def render(self, context):
        context[self.name] = self
        self.context = context.copy()
        return ''


class FunctionCall(Node):
    def __init__(self, name, args, procedure=False):
        self.name = name
        self.args = args
        self.procedure = procedure

    def render(self, context):
        func = self.lookup_context(context, self.name)
        if not func:
            raise Exception('Function {!r} not defined'
                .format('.'.join(self.name)))
        args = [arg.render(context) for arg in self.args]
        if self.procedure:
            return ''
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
    def __init__(self, value, parser):
        self.value = value
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
    def __init__(self, value):
        self.value = value
        self.rvalue = None

    def render(self, context):
        value = self.rvalue.render(context)
        context[self.value] = value
        return ''

    def __str__(self):
        return '{} - {} = {}\n'.format(type(self), str(self.value), str(self.rvalue))
