import sys
import os
import operator
from . import lexer


def context_lookup(context, name):
    ref = context.get(name[0])
    for part in name[1:]:
        ref = ref.get(part)
    return ref


class Parser():
    def __init__(self, code):
        self.lex = lexer.Lexer(code)
        self.tok = self.lex.get_token()

    def error(self, msg):
        self.lex.error(msg)

    def next_token(self):
        self.tok = self.lex.get_token()

    def consume(self, tok_val=''):
        if self.tok.value == tok_val:
            self.next_token()
        else:
            self.error('Expected a {!r}, '
                'got {!r} instead'.format(tok_val, self.tok.value))

    def identifier(self):
        if self.tok.type == lexer.IDENTIFIER:
            ident = self.tok.value
            self.next_token()
            return ident
        self.error('Identifier expected')

    def parse_name(self):
        name = [self.tok.value]
        self.next_token()
        while self.tok.value == lexer.DOT:
            self.next_token()
            name.append(self.identifier())
        if self.tok.value == lexer.OPEN_PARENS:
            node = self.function_call(name)
        elif name in lexer.BOOLEAN_VALUES:
            node = Boolean(name)
        else: 
            node = Variable(name)
        return node

    def factor(self):
        modifier = None
        if self.tok.is_addop():
            if self.tok.value == lexer.MINUS:
                modifier = UnaryMinus()
            self.next_token()

        if self.tok.type == lexer.NUMBER:
            node = Number(self.tok.value)
            self.next_token()
        elif self.tok.type == lexer.STRING:
            node = String(self.tok.value)
            self.next_token()
        elif self.tok.type == lexer.IDENTIFIER:
            node = self.parse_name()
        elif self.tok.value == lexer.OPEN_PARENS:
            self.consume(lexer.OPEN_PARENS)
            node = self.expression()
            self.consume(lexer.CLOSE_PARENS)
        else:
            self.error('Unexpected token {!r}'.format(self.tok.value))
        # prepend unary node if existent
        if modifier:
            modifier.child = node
            return modifier
        return node

    def multiplicative_expr(self):
        node = self.factor()
        while self.tok.is_mulop():
            if self.tok.value == lexer.MUL:
                self.next_token()
                rnode = self.factor()
                node = OpNode(node, rnode, operator.mul)
            elif self.tok.value == lexer.DIV:
                self.next_token()
                rnode = self.factor()
                node = OpNode(node, rnode, operator.floordiv)
            elif self.tok.value == lexer.MOD:
                self.next_token()
                rnode = self.factor()
                node = OpNode(node, rnode, operator.mod)
        return node

    def additive_expr(self):
        node = self.multiplicative_expr()
        while self.tok.is_addop():
            if self.tok.value == lexer.PLUS:
                self.next_token()
                rnode = self.multiplicative_expr()
                node = OpNode(node, rnode, operator.add)
            elif self.tok.value == lexer.MINUS:
                self.next_token()
                rnode = self.multiplicative_expr()
                node = OpNode(node, rnode, operator.sub)
        return node

    def relational_expr(self):
        node = self.additive_expr()
        while self.tok.is_relop():
            value = self.tok.value
            if value == lexer.GT:
                self.next_token()
                rnode = self.additive_expr()
                node = OpNode(node, rnode, operator.gt)
            elif value == lexer.GE:
                self.next_token()
                rnode = self.additive_expr()
                node = OpNode(node, rnode, operator.ge)
            elif value == lexer.LT:
                self.next_token()
                rnode = self.additive_expr()
                node = OpNode(node, rnode, operator.lt)
            elif value == lexer.LE:
                self.next_token()
                rnode = self.additive_expr()
                node = OpNode(node, rnode, operator.le)
        return node

    def equality_expr(self):
        node = self.relational_expr()
        while self.tok.is_equop():
            value = self.tok.value
            if value == lexer.EQUAL:
                self.consume(lexer.EQUAL)
                rnode = self.relational_expr()
                node = OpNode(node, rnode, operator.eq)
            elif value == lexer.DIFF:
                self.consume(lexer.DIFF)
                rnode = self.relational_expr()
                node = OpNode(node, rnode, operator.ne)
        return node

    def not_expr(self):
        if self.tok.value == lexer.BOOL_NOT:
            self.next_token()
            node = NotExpression()
            node.child = self.not_expr()
        else:
            node = self.equality_expr()
        return node

    def and_expr(self):
        node = self.not_expr()
        while self.tok.value == lexer.BOOL_AND:
            self.next_token()
            rnode = self.not_expr()
            node = AndExpression(node, rnode)
        return node

    def expression(self):
        node = self.and_expr()
        while self.tok.value == lexer.BOOL_OR:
            self.next_token()
            rnode = self.and_expr()
            node = OrExpression(node, rnode)
        return node

    def block(self, branch=False):
        block = BlockNode()
        self.consume(lexer.COLON)
        while self.tok.value not in (lexer.END, lexer.ELSE, lexer.EOF):
            block.add_child(self.statement())
        if self.tok.value == lexer.EOF:
            raise Exception('{!r} is missing, block not matched'.format(lexer.END))
        if not branch:
            self.consume(lexer.END)
        return block

    def assignment(self, name):
        self.consume(lexer.ASSIGN)
        node = Assignment(name)
        exp = self.expression()
        node.rvalue = exp
        self.consume(lexer.SEMICOLON)
        return node

    def if_stmt(self):
        self.next_token()
        exp_node = self.expression()
        node = Condition(exp_node)
        node.true_block = self.block(branch=True)
        if self.tok.value == lexer.ELSE:
            self.next_token()
            node.false_block = self.block()
        else:
            self.consume(lexer.END)
        return node

    def while_stmt(self):
        self.next_token()
        exp_node = self.expression()
        node = WhileLoop(exp_node)
        node.repeat_block = self.block()
        return node
    
    def print_stmt(self):
        self.next_token()
        exp_node = self.expression()
        self.consume(lexer.SEMICOLON)
        node = PrintCommand(exp_node)
        return node

    def include_stmt(self):
        self.next_token()
        exp_node = self.expression()
        self.consume(lexer.SEMICOLON)
        node = IncludeCommand(exp_node)
        return node

    def parse_stmt(self):
        self.next_token()
        exp_node = self.expression()
        self.consume(lexer.SEMICOLON)
        node = ParseCommand(exp_node)
        return node

    def params_list(self):
        params = []
        if self.tok.type == lexer.IDENTIFIER:
            params.append(self.tok.value)
        self.next_token()
        while self.tok.value == lexer.COMMA:
            self.consume(lexer.COMMA)
            if self.tok.type == lexer.IDENTIFIER:
                params.append(self.tok.value)
            else:
                self.error('Identifier expected')
            self.next_token()
        return params

    def function_definition(self):
        self.next_token()
        params = []
        name = self.identifier()
        self.consume(lexer.OPEN_PARENS)
        if self.tok.value != lexer.CLOSE_PARENS:
            params = self.params_list()
        self.consume(lexer.CLOSE_PARENS)
        body = self.block()
        node = Function(name, params, body)
        return node

    def expression_list(self):
        nodes = []
        if (self.tok.value == lexer.CLOSE_PARENS):
            return nodes
        node = self.expression()
        nodes.append(node)
        while self.tok.value == lexer.COMMA:
            self.consume(lexer.COMMA)
            node = self.expression()
            nodes.append(node)
        return nodes

    def function_call(self, name, procedure=False):
        self.consume(lexer.OPEN_PARENS)
        params = self.expression_list()
        self.consume(lexer.CLOSE_PARENS)
        return FunctionCall(name, params, procedure=procedure)

    def function_return(self):
        self.next_token()
        exp = self.expression()
        self.consume(lexer.SEMICOLON)
        return BlockReturn(exp)

    def statement(self):
        tok_type = self.tok.type
        node = None
        if tok_type == lexer.TEXT:
            node = Text(self.tok.value)
            self.next_token()
        elif tok_type == lexer.IDENTIFIER:
            name = self.tok.value
            self.next_token()
            next_token = self.tok.value
            if next_token == lexer.OPEN_PARENS:
                node = self.function_call(name, procedure=True)
                self.consume(lexer.SEMICOLON)
            elif next_token == lexer.ASSIGN:
                node = self.assignment(name)
            else:
                self.error('Invalid syntax')
        elif tok_type == lexer.KEYWORD:
            tok_val = self.tok.value
            stmt_map = {
                lexer.IF: self.if_stmt,
                lexer.WHILE: self.while_stmt,
                lexer.PRINT: self.print_stmt,
                lexer.INCLUDE: self.include_stmt,
                lexer.PARSE: self.parse_stmt,
                lexer.FUNCTION: self.function_definition,
                lexer.RETURN: self.function_return
            }
            node = stmt_map[tok_val]()
        else:
            self.error('Unexpected token [{!r}]'.format(self.tok.value))
        return node

    def parse(self):
        tree_root = BlockNode()
        while self.tok.type != lexer.EOF:
            node = self.statement()
            tree_root.add_child(node)
        return tree_root


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
            raise Exception('Variable {!r} not defined'.format(self.value))
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
            raise Exception('Function not defined')
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
    def __init__(self, exp):
        self.exp = exp

    def render(self, context):
        filename = self.exp.render(context)
        file_content = self.load_file(filename)
        try:
            subtree = Parser(file_content).parse()
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
