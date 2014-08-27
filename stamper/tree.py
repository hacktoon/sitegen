import os

def context_lookup(context, name):
    ref = context.get(name[0])
    for part in name[1:]:
        if not ref:
            return
        ref = ref.get(part)
    return ref


class Node():
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return '{} - [{}]\n'.format(type(self), str(self.value))


class BlockNode():
    def __init__(self):
        self.children = []
    
    def add_child(self, child):
        if type(child) == 'list':
            self.children.extend(child)
        else:
            self.children.append(child)

    def build_output(self, output_list):
        return ''.join(output_list)

    def render(self, context):
        output = []
        for child in self.children:
            output.append(str(child.render(context)))
            if isinstance(child, BlockReturn):
                return self.build_output(output)
        return self.build_output(output)

    def __str__(self):
        value = '{}\n'.format(type(self))
        for child in self.children:
            value += '\t{}'.format(str(child))
        return value


class OpNode():
    def __init__(self, left, right, op=None):
        self.left = left
        self.right = right
        self.op = op

    def render(self, context):
        left = self.left.render(context)
        right = self.right.render(context)
        return self.op(left, right)
    
    def __str__(self):
        value = '{}\n'.format(type(self))
        value += '\t{}\n'.format(str(self.left))
        value += '\t{}\n'.format(str(self.right))
        return value


class FileLoaderNode:
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


class Text(Node):
    def render(self, _):
        return self.value


class Variable(Node):
    def render(self, context):
        value = context_lookup(context, self.value)
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


class UnaryMinus():
    def __init__(self):
        self.child = None

    def add_child(self, child):
        self.child = child

    def render(self, context):
        return operator.neg(self.child.render(context))


class NotExpression():
    def __init__(self):
        self.child = None

    def add_child(self, child):
        self.child = child

    def render(self, context):
        return operator.not_(self.child.render(context))


class AndExpression(OpNode):
    def render(self, context):
        left = self.left.render(context)
        right = self.right.render(context)
        return left and right


class OrExpression(OpNode):
    def render(self, context):
        left = self.left.render(context)
        right = self.right.render(context)
        return left or right


class Condition():
    def __init__(self, exp):
        self.exp = exp
        self.true_block = None
        self.false_block = None

    def render(self, context):
        if self.exp.render(context):
            return self.true_block.render(context)
        elif self.false_block:
            return self.false_block.render(context) 
        else:
            return ''

    def __str__(self):
        true_block = str(self.true_block)
        false_block = str(self.false_block)
        return '{} cond: {}\n\t\ttrue: {}\n\t\tfalse: {}'.format(str(type(self)),
            str(self.exp), true_block, false_block)


class WhileLoop(BlockNode):
    def __init__(self, exp):
        self.exp = exp
        self.repeat_block = None

    def render(self, context):
        output = []
        while self.exp.render(context):
            text = self.repeat_block.render(context)
            output.append(text)
        return self.build_output(output)

    def __str__(self):
        return '{} cond: {}\n\t\tblock: {}'.format(str(type(self)),
            str(self.exp), str(self.repeat_block))


class ForLoop(BlockNode):
    def __init__(self, iter_name, collection):
        self.iter_name = iter_name
        self.collection = collection
        self.repeat_block = None

    def render(self, context):
        output = []
        collection = self.collection.render(context)
        for item in collection:
            for_context = context.copy()
            for_context[self.iter_name] = item
            text = self.repeat_block.render(for_context)
            output.append(text)
        return self.build_output(output)

    def __str__(self):
        return '{} \n\t\tblock: {}'.format(str(type(self)),
            str(self.repeat_block))


class Function():
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
        self.context = {}

    def call(self, args):
        received = len(args)
        expected = len(self.params)
        if expected > received:
            raise Exception('Expected {} params, '
                'received {}'.format(expected, received))
        scope_context = dict(zip(self.params, args))
        self.context.update(scope_context)
        return self.body.render(self.context)

    def render(self, context):
        context[self.name] = self
        self.context = context.copy()
        return ''

    def __str__(self):
        return '{}'.format(str(type(self)))


class FunctionCall(Node):
    def __init__(self, name, args, procedure=False):
        self.name = name
        self.args = args
        self.procedure = procedure

    def render(self, context):
        func = context_lookup(context, self.name)
        if not func:
            raise Exception('Function {!r} not defined'
                .format('.'.join(self.name)))
        args = [arg.render(context) for arg in self.args]
        if self.procedure:
            return ''
        return func.call(args)

    def __str__(self):
        return '{}'.format(str(type(self)))


class BlockReturn(Node):
    def __init__(self, exp):
        self.exp = exp

    def render(self, context):
        return self.exp.render(context)

    def __str__(self):
        return '{}'.format(str(type(self)))


class PrintCommand():
    def __init__(self, exp):
        self.exp = exp

    def render(self, context):
        return str(self.exp.render(context))

    def __str__(self):
        return '{}'.format(str(type(self)))


class IncludeCommand(FileLoaderNode):
    def __init__(self, exp):
        self.exp = exp

    def render(self, context):
        filename = self.exp.render(context)
        return self.load_file(filename)

    def __str__(self):
        return '{}'.format(str(type(self)))


class ParseCommand(FileLoaderNode):
    def __init__(self, exp, parser):
        self.exp = exp
        self.parser = parser

    def render(self, context):
        filename = self.exp.render(context)
        file_content = self.load_file(filename)
        try:
            subtree = self.parser(file_content).parse()
        except RuntimeError:
            sys.exit('{} is including itself.'.format(filename))
        return subtree.render(context)

    def __str__(self):
        return '{}'.format(str(type(self)))


class Assignment(Node):
    def __init__(self, value):
        super().__init__(value)
        self.rvalue = None

    def render(self, context):
        value = self.rvalue.render(context)
        context[self.value] = value
        return ''

    def __str__(self):
        return '{} - {} = {}\n'.format(type(self), str(self.value), str(self.rvalue))
