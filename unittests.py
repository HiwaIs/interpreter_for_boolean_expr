import unittest
from interpreter import *


# unittests for boolean interpreter


class TestBooInterpreter(unittest.TestCase):

    def set_up(self, text):
        self.lexer = Lexer('stdin', text)
        self.tokens, self.error = self.lexer.make_tokens()

        self.parser = Parser(self.tokens)
        self.ast = self.parser.parse()

        # Run program
        self.interpreter = Interpreter()
        self.result = self.interpreter.visit(self.ast.node)

        return self

    # convert intern bool into py bool
    def convert_bool(self):
        if self.result.value == 'TRUE':
            self.result = True
        else:
            self.result = False
        return self.result

    # convert token into strings
    def convert_tokens(self, list_of_tokens):
        for i in range(len(list_of_tokens)):
            if list_of_tokens[i].value == 'TRUE':
                list_of_tokens[i] = 'true'
            elif list_of_tokens[i].value == 'FALSE':
                list_of_tokens[i] = 'false'
            elif list_of_tokens[i].value == 'AND':
                list_of_tokens[i] = 'and'
            elif list_of_tokens[i].value == 'OR':
                list_of_tokens[i] = 'or'
            elif list_of_tokens[i].type == TT_NEG:
                list_of_tokens[i] = '!'
            elif list_of_tokens[i].type == TT_LK:
                list_of_tokens[i] = '('
            elif list_of_tokens[i].type == TT_RK:
                list_of_tokens[i] = ')'
            elif list_of_tokens[i].type == TT_EOF:
                list_of_tokens[i] = 'eof'

    def test_tokenlist(self):
        # enter manually
        self.text = "true and false"
        self.expected_list = ['true', 'and', 'false']
        # add last token 'EOF'
        self.expected_list.append('eof')

        self.lexer = Lexer('stdin', self.text)
        self.tokens, self.error = self.lexer.make_tokens()
        self.convert_tokens(self.tokens)

        self.assertEqual(self.tokens, self.expected_list)

    def test_expressions(self):
        self.set_up(
            "(!true and false or true and true or false and (true and false))")

        # convert intern bool into py bool
        self.result = self.convert_bool()

        self.assertEqual(False, self.result)

    def test_negation(self):
        neg_expr = "!!!true"
        neg_counter = 0
        bool_note = None
        self.set_up(neg_expr)
        for char in range(len(neg_expr)):
            if neg_expr[char] == 't':
                bool_note = True
                break
            elif neg_expr[char] == 'f':
                bool_note = False
                break
            else:
                neg_counter += 1

        # convert intern bool into py bool
        self.result = self.convert_bool()

        # Four cases:
        # True gets negated with even numbers of negations
        # True gets negated with uneven numbers of negations
        # False gets negated with even numbers of negations
        # False gets negated with even numbers of negations

        if bool_note:
            # case 1
            if neg_counter % 2 == 0:
                self.assertTrue(self.result)
            # case 2
            else:
                self.assertFalse(self.result)
        else:
            # case 3
            if neg_counter % 2 == 0:
                self.assertFalse(self.result)
            # case 4
            else:
                self.assertTrue(self.result)


if __name__ == '__main__':
    unittest.main()


# def setup

# def 'test ob tokenliste so erstellt wird wie erwartet'

# def 'test ob richtig gepartst wird'

# iein test für den interpreter noch'

# ausdrücke testen
# neg testen (sehr lang)

# neuer datetyp         randfalle wie fehler mit klammern
