


##########################
# POSSIBLE TOKENS
##########################

from string_with_arrows import *
from hashmap import *




TT_TRUE = 'TRUE'
TT_FALSE = 'FALSE'
TT_AND = 'AND'
TT_OR = 'OR'
TT_LK = '('
TT_RK = ')'
TT_NEG= '!'
TT_EOF = 'EOF'


hashmap = HashMap()

hashmap.put('TRUE', TT_TRUE)
hashmap.put('FALSE', TT_TRUE)
hashmap.put('AND', TT_AND)
hashmap.put('OR', TT_OR)
hashmap.put('(', TT_LK)
hashmap.put(')', TT_RK)
hashmap.put('!', TT_NEG)
hashmap.put('EOF', TT_EOF)


LETTERS = ['a','n','d', 'o', 'r', 't', 'e', 'u', 'f', 'l', 's']
BOOLEAN = 'ab'



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
		result  = f'{self.error_name}: {self.details}\n'
		result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
		result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result

class IllegalCharError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
	def __init__(self, pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


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

	def __repr__(self):
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
		self.current_char = self.text[self.pos.idx] if len(self.text) > self.pos.idx else None

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
			elif self.current_char == '!':
				tokens.append(Token(TT_NEG, pos_start=self.pos))
				self.advance()
			else:
				if self.current_char in LETTERS and self.peek_next() in LETTERS:
					tokens.append(self.make_word())
				else:
					pos_start = self.pos.copy()
					char = self.current_char
					self.advance()
					return [], IllegalCharError(pos_start, self.pos,"'" + char + "'" )

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
			return Token(word, word, pos_start, self.pos)
		
	def is_token_type(self, word):
		tokentype = hashmap.get(word)
		if tokentype == None:
			return False
		else:
			return True

	def peek_next(self):
		if self.pos.idx+1 >= len(self.text): return '\0'
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

class BooleanNode:
	def __init__ (self, tok):
		self.tok = tok

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'
	

class BinOpNode:
	def __init__(self, left_node: BooleanNode, op_tok, right_node: BooleanNode):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

		self.pos_start = self.left_node.pos_start
		self.pos_end = self.right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
	def __init__(self, op_tok, node: BooleanNode):
		self.op_tok = op_tok
		self.node = node

		self.pos_start = self.op_tok.pos_start
		self.pos_end = self.node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'



##########################
# PARSE RESULT
##########################

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None

	def register(self, res):
		if isinstance(res, ParseResult):
			if res.error: self.error = res.error
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
			"Expected 'and' or 'or'"
		))
		return res

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type == TT_NEG:
			res.register(self.advance())
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))

		elif tok.type in (TT_TRUE, TT_FALSE):
			res.register(self.advance())
			return res.success(BooleanNode(tok))

		elif tok.type == TT_LK:
			res.register(self.advance())
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == TT_RK:
				res.register(self.advance())
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
		))

		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected 'true' or 'false'"
		))



	def term(self):
		return self.bin_op(self.factor, TT_AND)


	def expr(self):
		return self.bin_op(self.term, TT_OR)

	def bin_op(self, func, op):
		res = ParseResult()
		left = res.register(func())
		if res.error: return res

		while self.current_tok.type == op:
			op_tok = self.current_tok
			res.register(self.advance())
			right = res.register(func())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)


##########################
# VALUES
##########################

class Booleen:
	def __init__(self, value):
		self.value = value

	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def and_to(self, other):
		if isinstance(other, Booleen):
			if self.value == other.value:
				return Booleen(self.value)
			return Booleen('FALSE')

	def or_to(self, other):
		if isinstance(other, Booleen):
			if self.value == 'FALSE' and other.value == 'FALSE':
				return Booleen(self.value)
			else:
				return Booleen('TRUE')

	def reverse(self):
		if self.value == 'TRUE':
			self.value = 'FALSE'
		elif self.value == 'FALSE':
			self.value = 'TRUE'

		return Booleen(self.value)

	def __repr__(self):
		return str(self.value)

##########################
# INTERPRETER
##########################

class Interpreter:
	def visit(self, node):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node)

	def no_visit_method(self, node):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	def visit_BooleanNode(self, node):
		return Booleen(node.tok.value).set_pos(node.pos_start, node.pos_end)


	def visit_BinOpNode(self, node):
		left = self.visit(node.left_node)
		right = self.visit(node.right_node)

		if node.op_tok.type == TT_AND:
			result = left.and_to(right)
		elif node.op_tok.type == TT_OR:
			result = left.or_to(right)

		return result.set_pos(node.pos_start, node.pos_end)


	def visit_UnaryOpNode(self, node):
	
		boolean = self.visit(node.node)

		if node.op_tok.type == TT_NEG:

			boolean = boolean.reverse()
		

		return boolean.set_pos(node.pos_start, node.pos_end)

##########################
# RUN
##########################

def run(fn, text):
	#Generate tokens
	lexer = Lexer(fn, text)
	tokens, error = lexer.make_tokens()
	print("tokenliste: " + str(tokens))
	if error: return None, error

	# Generate AST
	parser = Parser(tokens)
	ast = parser.parse()
	if ast.error: return None, ast.error

	# Run program
	interpreter = Interpreter()
	result = interpreter.visit(ast.node)

	return result, None
