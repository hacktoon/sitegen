import sys
import operator

from . import exceptions
from . import lexer
from .lexer import OPMAP
from . import tree


class Parser():
    def __init__(self, template, filename=''):
        self.template = template
        self.filename = filename
        self.tokens = lexer.Lexer().tokenize(template)
        self.tok_index = 0
        self.tok = self.tokens[self.tok_index]
        self.regions = {}
        self.base_template = None
        self.stmt_map = {
            lexer.IF: self.if_stmt,
            lexer.WHILE: self.while_stmt,
            lexer.LIST: self.list_stmt,
            lexer.REVLIST: self.revlist_stmt,
            lexer.PRINT: self.print_stmt,
            lexer.INCLUDE: self.include_stmt,
            lexer.PARSE: self.parse_stmt,
            lexer.FUNCTION: self.function_definition,
            lexer.RETURN: self.function_return,
            lexer.USE: self.use_stmt,
            lexer.REGION: self.region_stmt
        }

    def search_line_error(self, index):
        line = 1
        col = 1
        for i, char in enumerate(self.template):
            if index == i:
                return (line, col)
            if char == '\n':
                line += 1
                col = 1
            else:
                col += 1

    def error(self, msg, token=None):
        token = token or self.tok
        line, column = self.search_line_error(token.column)
        sys.exit('Error on file {!r}: {} at line {}, column {}'.format(
            self.filename, msg, line, column))

    def next_token(self):
        self.tok_index += 1
        try:
            self.tok = self.tokens[self.tok_index]
        except IndexError:
            self.tok = None

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

    def parse_identifier(self):
        token = self.tok
        tok_val = self.tok.value
        if tok_val in lexer.BOOLEAN_VALUES:
            self.next_token()
            return tree.Boolean(tok_val, token)
        self.next_token()
        if self.tok.value == lexer.OPEN_PARENS:
            return self.function_call(tok_val, token)
        else:
            return tree.Variable(tok_val, token)

    def factor(self):
        unary = None
        if self.tok.is_addop():
            if self.tok.value == lexer.MINUS:
                unary = tree.UnaryMinus(token=self.tok)
            self.next_token()
        if self.tok.type == lexer.NUMBER:
            node = tree.Number(self.tok.value, self.tok)
            self.next_token()
        elif self.tok.type == lexer.STRING:
            value = self.tok.value[1:-1] # remove quotes
            node = tree.String(value, self.tok)
            self.next_token()
        elif self.tok.type == lexer.IDENTIFIER:
            node = self.parse_identifier()
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
        token = self.tok
        node = self.factor()
        while self.tok.is_mulop():
            value = self.tok.value
            self.next_token()
            operands = [node, self.factor()]
            node = tree.Operation(OPMAP[value], token)
            node.add_child(operands)
        return node

    def additive_expr(self):
        token = self.tok
        node = self.multiplicative_expr()
        while self.tok.is_addop():
            value = self.tok.value
            self.next_token()
            operands = [node, self.multiplicative_expr()]
            node = tree.Operation(OPMAP[value], token)
            node.add_child(operands)
        return node

    def relational_expr(self):
        token = self.tok
        node = self.additive_expr()
        while self.tok.is_relop():
            value = self.tok.value
            self.next_token()
            operands = [node, self.additive_expr()]
            node = tree.Operation(OPMAP[value], token)
            node.add_child(operands)
        return node

    def equality_expr(self):
        token = self.tok
        node = self.relational_expr()
        while self.tok.is_equop():
            value = self.tok.value
            self.next_token()
            operands = [node, self.relational_expr()]
            node = tree.Operation(OPMAP[value], token)
            node.add_child(operands)
        return node

    def not_expr(self):
        token = self.tok
        if self.tok.value == lexer.BOOL_NOT:
            value = self.tok.value
            self.next_token()
            node = tree.Operation(OPMAP[value], token)
            node.add_child(self.not_expr())
        else:
            node = self.equality_expr()
        return node

    def and_expr(self):
        token = self.tok
        node = self.not_expr()
        while self.tok.value == lexer.BOOL_AND:
            value = self.tok.value
            self.next_token()
            operands = [node, self.not_expr()]
            node = tree.Operation(OPMAP[value], token)
            node.add_child(operands)
        return node

    def expression(self):
        token = self.tok
        node = self.and_expr()
        while self.tok.value == lexer.BOOL_OR:
            value = self.tok.value
            self.next_token()
            operands = [node, self.and_expr()]
            node = tree.Operation(OPMAP[value], token)
            node.add_child(operands)
        return node

    def stmt_block(self, branch=False):
        block = []
        self.consume(lexer.COLON)
        while self.tok.value not in (lexer.END, lexer.ELSE):
            block.append(self.statement())
        if not branch:
            self.consume(lexer.END)
        return block

    def assignment(self, name):
        self.consume(lexer.ASSIGN)
        node = tree.Assignment(name, self.tok)
        exp = self.expression()
        node.rvalue = exp
        return node

    def if_stmt(self):
        token = self.tok
        self.next_token()
        exp_node = self.expression()
        node = tree.Condition(exp_node, token)
        node.true_block = self.stmt_block(branch=True)
        if self.tok.value == lexer.ELSE:
            self.next_token()
            node.false_block = self.stmt_block()
        else:
            self.consume(lexer.END)
        return node

    def while_stmt(self):
        token = self.tok
        self.next_token()
        exp_node = self.expression()
        node = tree.WhileLoop(exp_node, token)
        node.add_child(self.stmt_block())
        return node

    def _list_stmt(self, reverse=False):
        token = self.tok
        self.next_token()
        collection = self.identifier()
        self.consume(lexer.AS)
        iter_name = self.identifier()
        node = tree.List(iter_name, collection, token, reverse)
        node.add_child(self.stmt_block())
        return node

    def revlist_stmt(self):
        return self._list_stmt()

    def list_stmt(self):
        return self._list_stmt(reverse=True)
    
    def print_stmt(self):
        token = self.tok
        self.next_token()
        exp_node = self.expression()
        node = tree.PrintCommand(exp_node, token)
        return node

    def include_stmt(self):
        token = self.tok
        self.next_token()
        exp_node = self.expression()
        node = tree.IncludeCommand(exp_node, token)
        return node

    def parse_stmt(self):
        token = self.tok
        self.next_token()
        exp_node = self.expression()
        node = tree.ParseCommand(exp_node, Parser, token)
        return node

    def use_stmt(self):
        self.next_token()
        if self.tok.type != lexer.STRING:
            self.error('String expected')
        self.base_template = self.tok.value[1:-1]
        self.next_token()
        return None

    def replace_region(self, node):
        if node.value in self.regions:
            return self.regions[node.value]
        return node

    def region_stmt(self):
        token = self.tok
        self.next_token()
        if self.tok.type != lexer.STRING:
            self.error('String expected')
        region_name = self.tok.value
        node = tree.Node(region_name, token)
        self.next_token()
        node.add_child(self.stmt_block())
        if self.base_template:
            # currently parsing a child template
            self.regions[region_name] = node
        else:
            # parsing a base template, replace regions by 
            # those defined in child template
            node = self.replace_region(node)
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
        token = self.tok
        self.next_token()
        params = []
        name = self.identifier()
        self.consume(lexer.OPEN_PARENS)
        if self.tok.value != lexer.CLOSE_PARENS:
            params = self.params_list()
        self.consume(lexer.CLOSE_PARENS)
        node = tree.Function(name, params, token)
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

    def function_call(self, name, token):
        self.consume(lexer.OPEN_PARENS)
        params = self.expression_list()
        self.consume(lexer.CLOSE_PARENS)
        return tree.FunctionCall(name, params, token)

    def function_return(self):
        token = self.tok
        self.next_token()
        exp = self.expression()
        return tree.ReturnCommand(exp, token)

    def statement(self):
        token = self.tok
        tok_type = self.tok.type
        node = None
        
        if tok_type == lexer.TEXT:
            node = tree.Text(self.tok.value, token)
            self.next_token()
        elif tok_type == lexer.TAG_VAR_OPEN:
            self.next_token()
            exp_node = self.expression()
            node = tree.PrintCommand(exp_node, token)
            self.consume(lexer.CLOSE_VAR)
        elif tok_type == lexer.IDENTIFIER:
            name = self.tok.value
            self.next_token()
            next_token = self.tok.value
            if next_token == lexer.OPEN_PARENS:
                node = self.function_call(name, token)
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

    def create_node(self, nodetype, *args):
        node = nodetype(*args)
        node.set_metadata()
        return node

    def parse(self, regions=None):
        self.regions = regions or {}
        tree_root = tree.Root(parser=self)

        while self.tok:
            node = self.statement()
            tree_root.add_child(node)
        # parse the base template and return it instead
        if self.base_template:
            try:
                fp = open(self.base_template, 'r')
            except IOError:
                self.error('File {!r} not found'.format(self.base_template))
            p = Parser(fp.read(), filename=self.base_template)
            fp.close()
            tree_root = p.parse(regions=self.regions)
        return tree_root