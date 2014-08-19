import sys
import tree
import operator

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

<unary-op> = + | -
<mult-op> = '*' | '/' | '%'
<add-op> = '+' | '-'
<rel op> = '<' | '<=' | '>=' | '>'
<eq-op> = '==' | '!='

'''

EOF = '\0'
NEWLINE = '\n'
STRING_DELIMITERS = ['"', "'"]
NUMBER = 'Number'
STRING = 'String'
IDENTIFIER = 'Identifier'
KEYWORD = 'Keyword'
SYMBOL = 'Symbol'
SYMBOLS_PERMITTED = list('+-*/=<>!%;,')
OPEN_PARENS = '('
CLOSE_PARENS = ')'
OPEN_BRACKET = '{'
CLOSE_BRACKET = '}'
EQUAL = '=='
DIFF = '!='
BOOLEAN_VALUES = ['true', 'false']
IF = 'if'
ELSE = 'else'
WHILE = 'while'
BOOL_OR = 'or'
BOOL_AND = 'and'
BOOL_NOT = 'not'
FUNCTION = 'function'
RETURN = 'return'
PRINT = 'print'
READ = 'read'
KEYWORDS = {'if', 'else', 'while', 'or', 
    'and', 'not', 'function', 'return',
    'print', 'read'
}

class Token():
    def __init__(self, val, type):
        self.value = val
        self.type = type

class Lexer():
    def __init__(self, code):
        self.index = 0
        self.code = code
        self.len = len(code)
        self.line = 1
        self.column = 1
        self.char = self.get_char()
    
    def get_char(self):
        if self.index >= self.len:
            return EOF
        char = self.code[self.index]
        self.column += 1
        self.index += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        return char

    def issymbol(self, c):
        return c in SYMBOLS_PERMITTED

    def next_char(self):
        self.char = self.get_char()

    def skip_whitespaces(self):
        while self.char.isspace():
            self.next_char()

    def error(self, msg):
        line = self.line
        column = self.column
        sys.exit('Error: {} at line {}, column {}'.format(msg, line, column))

    def get_number(self):
        num = ''
        while self.char.isdigit():
            num += self.char
            self.next_char()
        if self.char.isalpha():
            self.error('Invalid syntax')
        tok = Token(int(num), NUMBER)
        return tok

    def get_name(self):
        name = self.char
        self.next_char()
        while self.char.isalnum():
            name += self.char
            self.next_char()
        if name in KEYWORDS:
            tok = Token(name, KEYWORD)
        else:
            tok = Token(name, IDENTIFIER)
        return tok

    def get_string(self, delimiter):
        string_value = ''
        self.next_char()
        while self.char != delimiter:
            if self.char == EOF:
                self.error('String not properly closed')
            string_value += self.char
            self.next_char()
        self.next_char()
        return Token(string_value, STRING)

    def get_symbol(self):
        symbol = ''
        while self.issymbol(self.char):
            symbol += self.char
            self.next_char()
        tok = Token(symbol, SYMBOL)
        return tok

    def get_token(self):
        self.skip_whitespaces()
        tok = None
        if self.char.isdigit():
            tok = self.get_number()
        elif self.char.isalpha():
            tok = self.get_name()
        elif self.issymbol(self.char):
            tok = self.get_symbol()
        elif self.char in STRING_DELIMITERS:
            tok = self.get_string(self.char)
        elif self.char == OPEN_PARENS:
            tok = Token(self.char, OPEN_PARENS)
            self.next_char()
        elif self.char == CLOSE_PARENS:
            tok = Token(self.char, CLOSE_PARENS)
            self.next_char()
        elif self.char == OPEN_BRACKET:
            tok = Token(self.char, OPEN_BRACKET)
            self.next_char()
        elif self.char == CLOSE_BRACKET:
            tok = Token(self.char, CLOSE_BRACKET)
            self.next_char()
        elif self.char == NEWLINE:
            tok = Token(NEWLINE, NEWLINE)
            self.next_char()
        elif self.char == EOF:
            return Token(EOF, EOF)
        else:
            self.error('Unrecognized character')
        self.skip_whitespaces()
        return tok


class Parser():
    def __init__(self, code):
        self.lex = Lexer(code)
        self.tok = self.lex.get_token()
        self.table = {}

    def error(self, msg):
        self.lex.error(msg)

    def next_token(self):
        self.tok = self.lex.get_token()

    def is_addop(self):
        return self.tok.value in ['+', '-']

    def is_mulop(self):
        return self.tok.value in ['*', '/', '%']

    def is_equop(self):
        return self.tok.value in ['==', '!=']

    def is_relop(self):
        return self.tok.value in ['>', '>=', '<', '<=']

    def consume(self, tok_val=''):
        if self.tok.value == tok_val:
            self.next_token()
        else:
            self.error('Expected a {!r}, '
                'got {!r} instead'.format(tok_val, self.tok.value))

    def identifier(self):
        if self.tok.type == IDENTIFIER:
            ident = self.tok.value
            self.next_token()
            return ident
        self.error('Identifier expected')

    def factor(self):
        modifier = None
        if self.is_addop():
            if self.tok.value == '-':
                modifier = tree.UnaryMinus()
            self.next_token()

        if self.tok.type == NUMBER:
            node = tree.Number(self.tok.value)
            self.next_token()
        elif self.tok.type == STRING:
            node = tree.String(self.tok.value)
            self.next_token()
        elif self.tok.type == IDENTIFIER:
            name = self.tok.value
            self.next_token()
            if self.tok.type == OPEN_PARENS:
                node = self.function_call(name)
            elif name in BOOLEAN_VALUES:
                node = tree.Boolean(name)
            else: 
                node = tree.Variable(name)
        elif self.tok.value == OPEN_PARENS:
            self.consume(OPEN_PARENS)
            node = self.expression()
            self.consume(CLOSE_PARENS)
        else:
            self.error('Unexpected token {!r}'.format(self.tok.value))
        # prepend unary node if existent
        if modifier:
            modifier.child = node
            return modifier
        return node

    def multiplicative_expr(self):
        node = self.factor()
        while self.is_mulop():
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
        while self.is_addop():
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
        while self.is_relop():
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
        while self.is_equop():
            value = self.tok.value
            if value == EQUAL:
                self.consume(EQUAL)
                rnode = self.relational_expr()
                node = tree.OpNode(node, rnode, operator.eq)
            elif value == DIFF:
                self.consume(DIFF)
                rnode = self.relational_expr()
                node = tree.OpNode(node, rnode, operator.ne)
        return node

    def not_expr(self):
        if self.tok.value == BOOL_NOT:
            self.next_token()
            node = tree.NotExpression()
            node.child = self.not_expr()
        else:
            node = self.equality_expr()
        return node

    def and_expr(self):
        node = self.not_expr()
        while self.tok.value == BOOL_AND:
            self.next_token()
            rnode = self.not_expr()
            node = tree.AndExpression(node, rnode)
        return node

    def expression(self):
        node = self.and_expr()
        while self.tok.value == BOOL_OR:
            self.next_token()
            rnode = self.and_expr()
            node = tree.OrExpression(node, rnode)
        return node

    def block(self):
        block = tree.BlockNode()
        self.consume(OPEN_BRACKET)
        while self.tok.value != CLOSE_BRACKET:
            block.add_child(self.statement())
        self.consume(CLOSE_BRACKET)
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
        if self.tok.type == ELSE:
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
        if self.tok.type != IDENTIFIER:
            self.error('Identifier expected')
        name = self.tok.value
        self.next_token()
        self.consume(';')
        node = tree.ReadCommand(name)
        return node

    def params_list(self):
        params = []
        if self.tok.type == IDENTIFIER:
            params.append(self.tok.value)
        self.next_token()
        while self.tok.value == ',':
            self.consume(',')
            if self.tok.type == IDENTIFIER:
                params.append(self.tok.value)
            else:
                self.error('Identifier expected')
            self.next_token()
        return params

    def function_definition(self):
        self.next_token()
        params = []
        name = self.identifier()
        self.consume(OPEN_PARENS)
        if self.tok.value != CLOSE_PARENS:
            params = self.params_list()
        self.consume(CLOSE_PARENS)
        body = self.block()
        node = tree.Function(name, params, body)
        return node

    def expression_list(self):
        nodes = []
        if (self.tok.value == CLOSE_PARENS):
            return nodes
        node = self.expression()
        nodes.append(node)
        while self.tok.value == ',':
            self.consume(',')
            node = self.expression()
            nodes.append(node)
        return nodes

    def function_call(self, name):
        self.consume(OPEN_PARENS)
        params = self.expression_list()
        self.consume(CLOSE_PARENS)
        return tree.FunctionCall(name, params)

    def function_return(self):
        self.next_token()
        exp = self.expression()
        self.consume(';')
        return tree.BlockReturn(exp)

    def statement(self):
        tok_type = self.tok.type
        node = None
        if tok_type == NUMBER:
            if self.tok.value == ';':
                self.next_token()
        elif tok_type == IDENTIFIER:
            name = self.tok.value
            self.next_token()
            if self.tok.type == OPEN_PARENS:
                node = self.function_call(name)
                self.consume(';')
            elif self.tok.value == '=':
                node = self.assignment(name)
            else:
                node = tree.Variable(name)
        elif tok_type == KEYWORD:
            tok_val = self.tok.value
            if tok_val == IF:
                node = self.if_stmt()
            elif tok_val == WHILE:
                node = self.while_stmt()
            elif tok_val == PRINT:
                node = self.print_stmt()
            elif tok_val == READ:
                node = self.read_stmt()
            elif tok_val == FUNCTION:
                node = self.function_definition()
            elif tok_val == RETURN:
                node = self.function_return()
        else:
            self.error('Unrecognized token {!r}'.format(self.tok.value))
        return node

    def parse(self, tree_root):
        while self.tok.type != EOF:
            node = self.statement()
            tree_root.add_child(node)
        return tree_root


p = Parser(open(sys.argv[1]).read())
tree = p.parse(tree.BlockNode())

tree.render({})
