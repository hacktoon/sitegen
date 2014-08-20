import sys
import operator
from . import tree
from . import lexer

'''
<statement>  =  <conditional> | <while> | <assignment>
<assignment>  =  <identifier> '=' <expression>
<conditional>   = 'if' <expression> <block> ['else' <block>]
<while>   = 'while' <expression> <block>
-----
<expression> = <logical-and> | <logical-and> 'or' <logical-and> 
<logical-and> = <not-unary> | <not-unary> 'and' <not-unary>
<not-unary> = 'not' <not-unary> | <equality-expr>
<equality-expr> = <relational-expr> | <relational-expr> <eq-op> <relational-expr>
<relational-expr> = <additive-expr> | <additive-expr> <rel-op> <additive-expr>
<additive-expr> = <multiplicative-expr> | <multiplicative-expr> <add-op> <multiplicative-expr>
<multiplicative-expr> = <factor> | <factor> <mult-op> <factor>
<factor> :=  [<unary-op>] <literal> | ( <expression> )

<unary-op> = '+' | '-'
<mult-op> = '*' | '/' | '%'
<add-op> = '+' | '-'
<rel op> = '<' | '<=' | '>=' | '>'
<eq-op> = '==' | '!='

'''

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

    def factor(self):
        modifier = None
        if self.tok.is_addop():
            if self.tok.value == '-':
                modifier = tree.UnaryMinus()
            self.next_token()

        if self.tok.type == lexer.NUMBER:
            node = tree.Number(self.tok.value)
            self.next_token()
        elif self.tok.type == lexer.STRING:
            node = tree.String(self.tok.value)
            self.next_token()
        elif self.tok.type == lexer.IDENTIFIER:
            name = self.tok.value
            self.next_token()
            if self.tok.type == lexer.OPEN_PARENS:
                node = self.function_call(name)
            elif name in lexer.BOOLEAN_VALUES:
                node = tree.Boolean(name)
            else: 
                node = tree.Variable(name)
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
            if self.tok.value == '*':
                self.next_token()
                rnode = self.factor()
                node = tree.OpNode(node, rnode, operator.mul)
            elif self.tok.value == '/':
                self.next_token()
                rnode = self.factor()
                node = tree.OpNode(node, rnode, operator.floordiv)
            elif self.tok.value == '%':
                self.next_token()
                rnode = self.factor()
                node = tree.OpNode(node, rnode, operator.mod)
        return node

    def additive_expr(self):
        node = self.multiplicative_expr()
        while self.tok.is_addop():
            if self.tok.value == '+':
                self.next_token()
                rnode = self.multiplicative_expr()
                node = tree.OpNode(node, rnode, operator.add)
            elif self.tok.value == '-':
                self.next_token()
                rnode = self.multiplicative_expr()
                node = tree.OpNode(node, rnode, operator.sub)
        return node

    def relational_expr(self):
        node = self.additive_expr()
        while self.tok.is_relop():
            value = self.tok.value
            if value == '>':
                self.next_token()
                rnode = self.additive_expr()
                node = tree.OpNode(node, rnode, operator.gt)
            elif value == '>=':
                self.next_token()
                rnode = self.additive_expr()
                node = tree.OpNode(node, rnode, operator.ge)
            elif value == '<':
                self.next_token()
                rnode = self.additive_expr()
                node = tree.OpNode(node, rnode, operator.lt)
            elif value == '<=':
                self.next_token()
                rnode = self.additive_expr()
                node = tree.OpNode(node, rnode, operator.le)
        return node

    def equality_expr(self):
        node = self.relational_expr()
        while self.tok.is_equop():
            value = self.tok.value
            if value == lexer.EQUAL:
                self.consume(lexer.EQUAL)
                rnode = self.relational_expr()
                node = tree.OpNode(node, rnode, operator.eq)
            elif value == lexer.DIFF:
                self.consume(lexer.DIFF)
                rnode = self.relational_expr()
                node = tree.OpNode(node, rnode, operator.ne)
        return node

    def not_expr(self):
        if self.tok.value == lexer.BOOL_NOT:
            self.next_token()
            node = tree.NotExpression()
            node.child = self.not_expr()
        else:
            node = self.equality_expr()
        return node

    def and_expr(self):
        node = self.not_expr()
        while self.tok.value == lexer.BOOL_AND:
            self.next_token()
            rnode = self.not_expr()
            node = tree.AndExpression(node, rnode)
        return node

    def expression(self):
        node = self.and_expr()
        while self.tok.value == lexer.BOOL_OR:
            self.next_token()
            rnode = self.and_expr()
            node = tree.OrExpression(node, rnode)
        return node

    def block(self):
        block = tree.BlockNode()
        self.consume(lexer.OPEN_BRACKET)
        while self.tok.value != lexer.CLOSE_BRACKET:
            block.add_child(self.statement())
        self.consume(lexer.CLOSE_BRACKET)
        return block

    def assignment(self, name):
        self.consume('=')
        node = tree.Assignment(name)
        exp = self.expression()
        node.rvalue = exp
        self.consume(';')
        return node

    def if_stmt(self):
        self.next_token()
        exp_node = self.expression()
        node = tree.Condition(exp_node)
        node.true_block = self.block()
        if self.tok.type == lexer.ELSE:
            self.next_token()
            node.false_block = self.block()
        return node

    def while_stmt(self):
        self.next_token()
        exp_node = self.expression()
        node = tree.WhileLoop(exp_node)
        node.repeat_block = self.block()
        return node
    
    def print_stmt(self):
        self.next_token()
        exp_node = self.expression()
        self.consume(';')
        node = tree.PrintCommand(exp_node)
        return node

    def read_stmt(self):
        self.next_token()
        if self.tok.type != lexer.IDENTIFIER:
            self.error('Identifier expected')
        name = self.tok.value
        self.next_token()
        self.consume(';')
        node = tree.ReadCommand(name)
        return node

    def params_list(self):
        params = []
        if self.tok.type == lexer.IDENTIFIER:
            params.append(self.tok.value)
        self.next_token()
        while self.tok.value == ',':
            self.consume(',')
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
        node = tree.Function(name, params, body)
        return node

    def expression_list(self):
        nodes = []
        if (self.tok.value == lexer.CLOSE_PARENS):
            return nodes
        node = self.expression()
        nodes.append(node)
        while self.tok.value == ',':
            self.consume(',')
            node = self.expression()
            nodes.append(node)
        return nodes

    def function_call(self, name):
        self.consume(lexer.OPEN_PARENS)
        params = self.expression_list()
        self.consume(lexer.CLOSE_PARENS)
        return tree.FunctionCall(name, params)

    def function_return(self):
        self.next_token()
        exp = self.expression()
        self.consume(';')
        return tree.BlockReturn(exp)

    def statement(self):
        tok_type = self.tok.type
        node = None
        if tok_type == lexer.NUMBER:
            if self.tok.value == ';':
                self.next_token()
        elif tok_type == lexer.IDENTIFIER:
            name = self.tok.value
            self.next_token()
            if self.tok.type == lexer.OPEN_PARENS:
                node = self.function_call(name)
                self.consume(';')
            elif self.tok.value == '=':
                node = self.assignment(name)
            else:
                node = tree.Variable(name)
        elif tok_type == lexer.KEYWORD:
            tok_val = self.tok.value
            if tok_val == lexer.IF:
                node = self.if_stmt()
            elif tok_val == lexer.WHILE:
                node = self.while_stmt()
            elif tok_val == lexer.PRINT:
                node = self.print_stmt()
            elif tok_val == lexer.READ:
                node = self.read_stmt()
            elif tok_val == lexer.FUNCTION:
                node = self.function_definition()
            elif tok_val == lexer.RETURN:
                node = self.function_return()
        else:
            self.error('Unrecognized token {!r}'.format(self.tok.value))
        return node

    def parse(self, tree_root=None):
        if not tree_root:
            tree_root = tree.BlockNode()
        while self.tok.type != lexer.EOF:
            node = self.statement()
            tree_root.add_child(node)
        return tree_root


#p = Parser(open(sys.argv[1]).read())
#tree = p.parse()

#tree.render({})
