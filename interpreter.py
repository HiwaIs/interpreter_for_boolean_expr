
##########################
# POSSIBLE TOKENS
##########################

from hashmap import HashMap
from string_with_arrows import *
from keyword import *
import string
import types


# Token Types
TT_KEYWORD = 'KEYWORD'
TT_IDENTIFIER = 'IDENTIFIER'
TT_LK = '('
TT_RK = ')'
TT_NEG = '!'
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_EE = '=='
TT_NE = '!='
TT_LT = '<'
TT_GT = '>'
TT_LTE = '<='
TT_GTE = '>='
TT_EOF = 'EOF'


def isEven(arg):
    return (arg % 2) == 0


def isNotEven(arg):
    return (arg % 2) != 0


def reverse(arg):
    if arg == 'TRUE':
        arg = True
    else:
        arg = False


keyword = HashMap()
keyword.put('TRUE', TT_KEYWORD)
keyword.put('FALSE', TT_KEYWORD)
keyword.put('AND', TT_KEYWORD)
keyword.put('OR', TT_KEYWORD)

identifier = HashMap()
identifier.put('A', 1)
identifier.put('B', 2)
identifier.put('C', 3)
identifier.put('ISEVEN', isEven)
identifier.put('ISNOTEVEN', isNotEven)

LETTERS = string.ascii_letters
DIGITS = '0123456789'
LETTERS_AND_DIGITS = LETTERS + DIGITS

##########################
# ERRORS
##########################


class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + \
            string_with_arrows(self.pos_start.ftxt,
                               self.pos_start, self.pos_end)
        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)


class NonExistentIdentifierError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Nonexistent Identifier', details)


class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Expected Character', details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n\n' + \
            string_with_arrows(self.pos_start.ftxt,
                               self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result


##########################
# POSITION
##########################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

##########################
# TOKEN
##########################


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


##########################
# LEXER
##########################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if len(
            self.text) > self.pos.idx else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LK, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RK, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!' and self.peek_next() != '=':
                tokens.append(Token(TT_NEG, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!' and self.peek_next() == '=':
                token, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char == '=':
                token, error = self.make_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            else:
                if self.current_char in LETTERS:
                    token, error = self.make_word()
                    if error:
                        return [], error
                    tokens.append(token)
                elif self.current_char in DIGITS:
                    tokens.append(self.make_number())
                else:
                    pos_start = self.pos.copy()
                    char = self.current_char
                    self.advance()
                    return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_word(self):
        word = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS:
            word += self.current_char
            self.advance()

        word = word.upper()
        if self.is_token_type(word):
            return Token(TT_KEYWORD, word, pos_start, self.pos), None
        else:
            print("ich mach das")
            return Token(TT_IDENTIFIER, identifier.get(word), pos_start, self.pos), None

    def check_identifier(self, word):
        word_identifier = identifier.get(word)

        if word_identifier:
            return True
        else:
            return False

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

        # self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_equals(self):
        tok_type = None
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE
            return Token(tok_type, pos_start=pos_start, pos_end=self.pos), None

        else:
            return None, ExpectedCharError(pos_start, self.pos, "'=' (after '=')")

    def make_less_than(self):
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def is_token_type(self, word):
        tokentype = keyword.get(word)
        if tokentype == None:
            return False
        else:
            return True

    def peek_next(self):
        if self.pos.idx+1 >= len(self.text):
            return '\0'
        return self.text[self.pos.idx+1]

    def next_char_is_end(self):
        if self.pos.idx + 1 > len(self.text):
            return True
        else:
            return False

    def is_at_end(self):
        if self.pos.idx > len(self.text):
            return True
        else:
            return False

##########################
# NODES
##########################


class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class BooleanNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if self.arg_nodes:
            self.pos_end = self.arg_nodes.pos_end
        else:
            self.pos_end = self.node_to_call.pos_end


class VarNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.var_name_tok_value = var_name_tok.value

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

##########################
# PARSE RESULT
##########################


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

##########################
# PARSER
##########################


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'and', 'or', logical comparsions or equality requests"
            ))
        return res

    def peek_prev(self):
        return self.tokens[self.tok_idx - 1]

    def equality(self):
        return self.bin_op(self.comparsion, (TT_EE, TT_NE))

    def comparsion(self):
        return self.bin_op(self.unary, (TT_LT, TT_LTE, TT_GT, TT_GTE))

    def unary(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type == TT_NEG:
            res.register(self.advance())
            unary = res.register(self.unary())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, unary))

        call = res.register(self.call())
        if res.error:
            return res

        return res.success(call)

    def call(self):
        res = ParseResult()
        primary = res.register(self.primary())
        if res.error:
            return res

        if self.current_tok.type == TT_LK:
            res.register(self.advance())
            arg_nodes = None

            if self.current_tok.type == TT_RK:
                res.register(self.advance())

            else:
                arg_nodes = res.register(self.primary())
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Excepted ')', int, float, identifier or '('"
                    ))

                if self.current_tok.type != TT_RK:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ')'"
                    ))

                res.register(self.advance())
            return res.success(CallNode(primary, arg_nodes))
        return res.success(primary)

    def primary(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type == TT_KEYWORD and (tok.value == 'TRUE' or tok.value == 'FALSE'):
            res.register(self.advance())
            return res.success(BooleanNode(tok))

        elif tok.type in (TT_INT, TT_FLOAT):

            res.register(self.advance())
            return res.success(NumberNode(tok))

        elif tok.type == TT_LK:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TT_RK:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        elif tok.type == TT_IDENTIFIER:
            print("ich bin hier im")
            if tok.value == None:
                print("ist none")
                return res.failure(NonExistentIdentifierError(
                    tok.pos_start, tok.pos_end, "Unknown Identifier"))
            res.register(self.advance())
            if isinstance(tok.value, int):
                return res.success(NumberNode(tok))
            elif tok.value == 'TRUE' or tok.value == 'FALSE':
                return res.success(BooleanNode(tok))
            elif isinstance(tok.value, types.FunctionType):
                return res.success(tok)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected 'true', 'false', 'identifier', 'INT' or 'FLOAT'"
        ))

    def term(self):
        return self.bin_op(self.equality, keyword.get('AND'))

    def expr(self):
        return self.bin_op(self.term, keyword.get('OR'))

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

##########################
# VALUES
##########################


class RTResult:
    def __init__(self):
        self.error = None
        self.value = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

##########################
# VALUES
##########################


class Booleen:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def and_to(self, other):
        if isinstance(other, Booleen):
            if self.value == other.value:
                return Booleen(self.value).set_context(self.context), None
            return Booleen('FALSE').set_context(self.context), None
        else:
            return None, self.cant_compare_error(other)

    def or_to(self, other):
        if isinstance(other, Booleen):
            if self.value == 'FALSE' and other.value == 'FALSE':
                return Booleen(self.value).set_context(self.context), None
            else:
                return Booleen('TRUE').set_context(self.context), None
        else:
            return None, self.cant_compare_error(other)

    def reverse(self):
        if self.value == 'TRUE':
            self.value = 'FALSE'
        elif self.value == 'FALSE':
            self.value = 'TRUE'

        return Booleen(self.value).set_context(self.context), None

    def not_equal(self, other):
        if not (isinstance(other, Booleen)):
            return None, self.cant_compare_error(other)
        else:
            if self.value != other.value:
                return Booleen('TRUE').set_context(self.context), None
            else:
                return Booleen('FALSE').set_context(self.context), None

    def double_equal(self, other):
        if not (isinstance(other, Booleen)):
            return None, self.cant_compare_error(other)
        else:
            if self.value == other.value:
                return Booleen('TRUE').set_context(self.context), None
            else:
                return Booleen('FALSE').set_context(self.context), None

    def __repr__(self):
        return str(self.value)

    def cant_compare_error(self, other):
        return RTError(
            other.pos_start, other.pos_end,
            "Comparsion of 'bool' and 'int/float'",
            self.context
        )


class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def not_equal(self, other):
        if self.value != other.value:
            return Booleen('TRUE').set_context(self.context), None
        else:
            return Booleen('FALSE').set_context(self.context), None

    def double_equal(self, other):
        if self.value == other.value:
            return Booleen('TRUE').set_context(self.context), None
        else:
            return Booleen('FALSE').set_context(self.context), None

    def less_than(self, other):
        if not (isinstance(other, Number)):
            return None, self.cant_compare_error(other)
        else:
            if self.value < other.value:
                return Booleen('TRUE').set_context(self.context), None
            else:
                return Booleen('FALSE').set_context(self.context), None

    def less_equal_than(self, other):
        if not (isinstance(other, Number)):
            return None, self.cant_compare_error(other)
        else:
            if self.value <= other.value:
                return Booleen('TRUE').set_context(self.context), None
            else:
                return Booleen('FALSE').set_context(self.context), None

    def greater_than(self, other):
        if not (isinstance(other, Number)):
            return None, self.cant_compare_error(other)
        else:
            if self.value > other.value:
                return Booleen('TRUE').set_context(self.context), None
            else:
                return Booleen('FALSE').set_context(self.context), None

    def greater_equal_than(self, other):
        if not (isinstance(other, Number)):
            return None, self.cant_compare_error(other)
        else:
            if self.value >= other.value:
                return Booleen('TRUE').set_context(self.context), None
            else:
                return Booleen('FALSE').set_context(self.context), None

    def not_equal(self, other):
        if not (isinstance(other, Number)):
            return None, self.cant_compare_error(other)
        else:
            if self.value != other.value:
                return Booleen('TRUE').set_context(self.context), None
            else:
                return Booleen('FALSE').set_context(self.context), None

    def double_equal(self, other):
        if not (isinstance(other, Number)):
            return None, self.cant_compare_error(other)
        else:
            if self.value == other.value:
                return Booleen('TRUE').set_context(self.context), None
            else:
                return Booleen('FALSE').set_context(self.context), None

    def cant_compare_error(self, other):
        return RTError(
            other.pos_start, other.pos_end,
            "Comparsion of 'int/float' and 'bool'",
            self.context
        )

    def __repr__(self):
        return str(self.value)

##########################
# CONTEXT
##########################


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.hashmap = None


##########################
# INTERPRETER
##########################

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_BooleanNode(self, node, context):
        return RTResult().success(
            Booleen(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        type_of_left = type(left)
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res

        if node.op_tok.matches(TT_KEYWORD, 'AND'):
            result, error = left.and_to(right)
        elif node.op_tok.matches(TT_KEYWORD, 'OR'):
            result, error = left.or_to(right)

        elif isinstance(left, Number) and node.op_tok.type != TT_EE and node.op_tok.type != TT_NE:
            if node.op_tok.type == TT_LT:
                result, error = left.less_than(right)
            elif node.op_tok.type == TT_LTE:
                result, error = left.less_equal_than(right)
            elif node.op_tok.type == TT_GT:
                result, error = left.greater_than(right)
            elif node.op_tok.type == TT_GTE:
                result, error = left.greater_equal_than(right)

        elif node.op_tok.type == TT_EE:
            result, error = left.double_equal(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.not_equal(right)
        else:
            error = RTError(
                left.pos_start, left.pos_end,
                f'The type "{type_of_left}" has no operation "{node.op_tok}"',
                context
            )

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        boolean = res.register(self.visit(node.node, context))
        error = None
        if isinstance(boolean, Booleen):
            if node.op_tok.type == TT_NEG:
                boolean, error = boolean.reverse()
        else:
            error = RTError(
                node.pos_start, node.pos_end,
                "Expected 'true' or 'false' after '!'",
                context
            )
        if error:
            return res.failure(error)
        else:
            return res.success(boolean.set_pos(node.pos_start, node.pos_end))

    def visit_CallNode(self, node, context):
        res = RTResult()
        arg = None
        error = None

        value_to_call = node.node_to_call.value

        arg = res.register(self.visit(node.arg_nodes, context))
        if not isinstance(arg, Number):
            error = RTError(
                arg.pos_start, arg.pos_end,
                "Method only works with arguments from type 'Number'",
                context
            )

        if isinstance(arg, Number):
            arg = int(arg.value)
            value_to_call = value_to_call(arg)

        if value_to_call == True:
            value_to_call = Booleen('TRUE').set_context(context)
        elif value_to_call == False:
            value_to_call = Booleen('FALSE').set_context(context)

        if error:
            return res.failure(error)
        return res.success(value_to_call.set_pos(node.pos_start, node.pos_end))

##########################
# RUN
##########################


def run(fn, text):
    # Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    print("tokenliste: " + str(tokens))
    if error:
        return None, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    # Run program
    interpreter = Interpreter()
    context = Context('<program>')
    context.identifier = identifier
    result = interpreter.visit(ast.node, context)

    return result.value, result.error


# run method for testing the parser

# def run(fn, text):
#     # Generate tokens
#     lexer = Lexer(fn, text)
#     tokens, error = lexer.make_tokens()
#     if error:
#         return None, error

#     # Generate AST
#     parser = Parser(tokens)
#     ast = parser.parse()

#     return ast.node, ast.error
