import operator
import sys

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

    def render(self, context):
        for child in self.children:
            if isinstance(child, BlockReturn):
                return child.render(context)
            child.render(context)

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


class Text(Node):
    def render(self, context):
        return self.value


class Variable(Node):
    def render(self, context):
        if not self.value in context.keys():
            raise Exception('Variable {!r} not defined'.format(self.value))
        return context.get(self.value)


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
           self.true_block.render(context) 
        elif self.false_block:
           self.false_block.render(context) 

    def __str__(self):
        true_block = str(self.true_block)
        false_block = str(self.false_block)
        return '{} cond: {}\n\t\ttrue: {}\n\t\tfalse: {}'.format(str(type(self)),
            str(self.exp), true_block, false_block)


class WhileLoop():
    def __init__(self, exp):
        self.exp = exp
        self.repeat_block = None

    def render(self, context):
        while self.exp.render(context):
           self.repeat_block.render(context)

    def __str__(self):
        return '{} cond: {}\n\t\tblock: {}'.format(str(type(self)),
            str(self.exp), str(self.repeat_block))


class Function():
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
        self.context = {}

    def call(self, args):
        if len(self.params) > len(args):
            raise Exception('Expected more params')
        scope_context = dict(zip(self.params, args))
        self.context.update(scope_context)
        return self.body.render(self.context)

    def render(self, context):
        context[self.name] = self
        self.context = context.copy()

    def __str__(self):
        return '{}'.format(str(type(self)))


class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def render(self, context):
        if not self.name in context.keys():
            raise Exception('Function not defined')
        args = [arg.render(context) for arg in self.args]
        return context[self.name].call(args)

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
        print(self.exp.render(context))

    def __str__(self):
        return '{}'.format(str(type(self)))


class ReadCommand():
    def __init__(self, variable):
        self.variable = variable

    def render(self, context):
        value = input()
        context[self.variable] = value

    def __str__(self):
        return '{}'.format(str(type(self)))


class Assignment(Node):
    def __init__(self, value):
        super().__init__(value)
        self.rvalue = None

    def render(self, context):
        value = self.rvalue.render(context)
        context[self.value] = value

    def __str__(self):
        return '{} - {} = {}\n'.format(type(self), str(self.value), str(self.rvalue))
