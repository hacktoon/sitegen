import sys
import operator

from . import lexer
from .lexer import OPMAP
from . import tree


class Parser():
    def __init__(self, code):
        self.lex = lexer.Lexer(code)
        self.tok = self.lex.get_token()
        self.stmt_map = {
            lexer.IF: self.if_stmt,
            lexer.WHILE: self.while_stmt,
            lexer.LIST: self.list_stmt,
            lexer.REVLIST: self.revlist_stmt,
            lexer.PRINT: self.print_stmt,
            lexer.INCLUDE: self.include_stmt,
            lexer.PARSE: self.parse_stmt,
            lexer.FUNCTION: self.function_definition,
            lexer.RETURN: self.function_return
        }

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
            node = tree.Boolean(name)
        else: 
            node = tree.Variable(name)
        return node

    def factor(self):
        unary = None
        if self.tok.is_addop():
            if self.tok.value == lexer.MINUS:
                unary = tree.UnaryMinus()
            self.next_token()

        if self.tok.type == lexer.NUMBER:
            node = tree.Number(self.tok.value)
            self.next_token()
        elif self.tok.type == lexer.STRING:
            node = tree.String(self.tok.value)
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
        if unary:
            unary.add_child(node)
            return unary
        return node

    def multiplicative_expr(self):
        node = self.factor()
        while self.tok.is_mulop():
            value = self.tok.value    
            self.next_token()
            operands = [node, self.factor()]
            node = tree.Operation(OPMAP[value])
            node.add_child(operands)
        return node

    def additive_expr(self):
        node = self.multiplicative_expr()
        while self.tok.is_addop():    
            value = self.tok.value
            self.next_token()
            operands = [node, self.multiplicative_expr()]
            node = tree.Operation(OPMAP[value])
            node.add_child(operands)
        return node

    def relational_expr(self):
        node = self.additive_expr()
        while self.tok.is_relop():
            value = self.tok.value
            self.next_token()
            operands = [node, self.additive_expr()]
            node = tree.Operation(OPMAP[value])
            node.add_child(operands)
        return node

    def equality_expr(self):
        node = self.relational_expr()
        while self.tok.is_equop():
            value = self.tok.value
            self.next_token()
            operands = [node, self.relational_expr()]
            node = tree.Operation(OPMAP[value])
            node.add_child(operands)
        return node

    def not_expr(self):
        if self.tok.value == lexer.BOOL_NOT:
            value = self.tok.value
            self.next_token()
            node = tree.Operation(OPMAP[value])
            node.add_child(self.not_expr())
        else:
            node = self.equality_expr()
        return node

    def and_expr(self):
        node = self.not_expr()
        while self.tok.value == lexer.BOOL_AND:
            value = self.tok.value
            self.next_token()
            operands = [node, self.not_expr()]
            node = tree.Operation(OPMAP[value])
            node.add_child(operands)
        return node

    def expression(self):
        node = self.and_expr()
        while self.tok.value == lexer.BOOL_OR:
            value = self.tok.value
            self.next_token()
            operands = [node, self.and_expr()]
            node = tree.Operation(OPMAP[value])
            node.add_child(operands)
        return node

    def stmt_block(self, branch=False):
        block = []
        self.consume(lexer.COLON)
        while self.tok.value not in (lexer.END, lexer.ELSE, lexer.EOF):
            block.append(self.statement())
        if self.tok.value == lexer.EOF:
            raise Exception('{!r} is missing, '
                'block not matched'.format(lexer.END))
        if not branch:
            self.consume(lexer.END)
        return block

    def assignment(self, name):
        self.consume(lexer.ASSIGN)
        node = tree.Assignment(name)
        exp = self.expression()
        node.rvalue = exp
        self.consume(lexer.SEMICOLON)
        return node

    def if_stmt(self):
        self.next_token()
        exp_node = self.expression()
        node = tree.Condition(exp_node)
        node.true_block = self.stmt_block(branch=True)
        if self.tok.value == lexer.ELSE:
            self.next_token()
            node.false_block = self.stmt_block()
        else:
            self.consume(lexer.END)
        return node

    def while_stmt(self):
        self.next_token()
        exp_node = self.expression()
        node = tree.WhileLoop(exp_node)
        node.add_child(self.stmt_block())
        return node

    def _list_stmt(self, reverse=False):
        self.next_token()
        collection = self.identifier()
        self.consume(lexer.AS)
        iter_name = self.identifier()
        node = tree.List(iter_name, collection, reverse)
        node.add_child(self.stmt_block())
        return node

    def revlist_stmt(self):
        return self._list_stmt()

    def list_stmt(self):
        return self._list_stmt(reverse=True)
    
    def print_stmt(self):
        self.next_token()
        exp_node = self.expression()
        self.consume(lexer.SEMICOLON)
        node = tree.PrintCommand(exp_node)
        return node

    def include_stmt(self):
        self.next_token()
        exp_node = self.expression()
        self.consume(lexer.SEMICOLON)
        node = tree.IncludeCommand(exp_node)
        return node

    def parse_stmt(self):
        self.next_token()
        exp_node = self.expression()
        self.consume(lexer.SEMICOLON)
        node = tree.ParseCommand(exp_node, Parser)
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
        node = tree.Function(name, params)
        node.add_child(self.stmt_block())
        return node

    def expression_list(self):
        # parse a list of expressions
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
        return tree.FunctionCall(name, params, procedure=procedure)

    def function_return(self):
        self.next_token()
        exp = self.expression()
        self.consume(lexer.SEMICOLON)
        return tree.BlockReturn(exp)

    def statement(self):
        tok_type = self.tok.type
        node = None
        if tok_type == lexer.TEXT:
            node = tree.Text(self.tok.value)
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
            node = self.stmt_map[tok_val]()
        else:
            self.error('Unexpected token [{!r}]'.format(self.tok.value))
        return node

    def parse(self):
        tree_root = tree.Node()
        while self.tok.type != lexer.EOF:
            node = self.statement()
            tree_root.add_child(node)
        return tree_root