"""
 This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import typing

import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    op = ['=', '+', '-', '/', '|', '~', '^', '#', '*', '&gt;', '&lt;', '&quot;', '&amp;']
    unaryOp = ['-', '~']

    def __init__(self, input_stream: JackTokenizer, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")

        self.tokenizer = input_stream
        self.output_XML = output_stream
        self.advanceT()
        self.tab_num = 0
        self.compile_class()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        self.eat("class")
        self.writeLS("class")
        self.writeT(self.curr_token)
        self.advanceT()
        self.writeT(self.curr_token)
        self.advanceT()
        self.open_close_brackets_class()
        self.writeLE("class")

    def compile_class_var_dec(self) -> None:  # static / field
        """Compiles a static declaration or a field declaration."""
        self.writeLS("classVarDec")
        self.writeT(self.curr_token)  # ststic/field
        self.advanceT()
        self.writeT(self.curr_token)  # type
        self.advanceT()
        self.writeT(self.curr_token)  # name
        self.advanceT()
        while self.curr_token[1] == ',':
            self.writeT(self.curr_token)  # ,
            self.advanceT()
            self.writeT(self.curr_token)  # next var
            self.advanceT()
        self.line_end()
        self.writeLE('classVarDec')

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.writeLS("subroutineDec")
        self.writeT(self.curr_token)  # method, function, or constructor
        self.advanceT()
        self.writeT(self.curr_token)  # ret type
        self.advanceT()
        self.writeT(self.curr_token)  # sub name
        self.advanceT()
        self.eat('(')
        self.writeT(self.curr_token)
        self.advanceT()
        self.compile_parameter_list()
        self.eat(')')
        self.writeT(self.curr_token)
        self.advanceT()
        self.writeLS("subroutineBody")
        self.eat('{')
        self.writeT(self.curr_token)  # {
        self.advanceT()
        while self.curr_token[1] == 'var':
            self.compile_var_dec()
        self.compile_statements()  # statments of the method, function, or constructor
        self.eat('}')
        self.writeT(self.curr_token)
        self.advanceT()
        self.writeLE("subroutineBody")
        self.writeLE("subroutineDec")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.writeLS("parameterList")
        while self.curr_token[1] != ')':
            self.writeT(self.curr_token)  # type
            self.advanceT()
            self.writeT(self.curr_token)  # var name
            self.advanceT()
            if self.curr_token[1] == ',':
                self.writeT(self.curr_token)  # ,
                self.advanceT()
        self.writeLE("parameterList")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        self.writeLS("varDec")
        self.eat("var")
        self.writeT(self.curr_token)  # var
        self.advanceT()
        self.writeT(self.curr_token)  # type
        self.advanceT()
        self.writeT(self.curr_token)  # name
        self.advanceT()
        while self.curr_token[1] == ',':
            self.writeT(self.curr_token)  # ,
            self.advanceT()
            self.writeT(self.curr_token)  # type
            self.advanceT()
            self.writeT(self.curr_token)  # name
            self.advanceT()
        self.line_end()
        self.writeLE("varDec")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        self.writeLS("statements")
        while self.curr_token[1] != '}':
            self.compile_statement()
        self.writeLE("statements")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.eat('do')
        self.writeLS("doStatement")
        self.writeT(self.curr_token)  # do
        self.advanceT()
        self.do_subroutineCall()
        self.line_end()  # ;
        self.writeLE("doStatement")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.eat('let')
        self.writeLS("letStatemant")
        self.writeT(self.curr_token)  # let
        self.advanceT()
        self.writeT(self.curr_token)  # var name
        self.advanceT()
        if self.curr_token[1] == '[':
            self.eat('[')
            self.writeT(self.curr_token)  # [
            self.advanceT()
            self.compile_expression()
            self.eat(']')
            self.writeT(self.curr_token)  # ]
            self.advanceT()
        self.eat("=")
        self.writeT(self.curr_token)  # =
        self.advanceT()
        self.compile_expression()
        self.line_end()
        self.writeLE("letStatemant")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.eat("while")
        self.writeLS("whileStaement")
        self.writeT(self.curr_token)  # while
        self.advanceT()
        self.eat('(')
        self.writeT(self.curr_token)
        self.advanceT()
        self.compile_expression()
        self.eat(')')
        self.writeT(self.curr_token)
        self.advanceT()
        self.eat('{')
        self.writeT(self.curr_token)
        self.advanceT()
        self.compile_statements()
        self.eat('}')
        self.writeT(self.curr_token)
        self.advanceT()
        self.writeLE("while")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.eat("return")
        self.writeLS("returnStatement")
        self.writeT(self.curr_token)  # return
        self.advanceT()
        if self.curr_token[1] != (';'):
            self.compile_expression()
        self.line_end()
        self.writeLE("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.eat("if")
        self.writeLS("if")
        self.writeT(self.curr_token)  # if
        self.advanceT()
        self.eat('(')
        self.writeT(self.curr_token)
        self.advanceT()
        self.compile_expression()
        self.eat(')')
        self.writeT(self.curr_token)
        self.advanceT()
        self.eat('{')
        self.writeT(self.curr_token)
        self.advanceT()
        self.compile_statements()
        self.eat('}')
        self.writeT(self.curr_token)
        self.advanceT()
        if self.curr_token[1] == "else":
            self.eat("else")
            self.writeT(self.curr_token)
            self.advanceT()
            self.eat('{')
            self.writeT(self.curr_token)
            self.advanceT()
            self.compile_statements()
            self.eat('}')
            self.writeT(self.curr_token)
            self.advanceT()
            self.compile_statements()
        self.writeLE("if")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.writeLS("expression")
        self.compile_term()
        while self.curr_token[1] in CompilationEngine.op:
            self.writeT(self.curr_token)  # op
            self.advanceT()
            self.compile_term()
        self.writeLE("expression")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.writeLS("term")
        self.writeT(self.curr_token)  # term
        self.advanceT()
        if self.curr_token[1] == "(":
            self.eat('(')
            self.writeT(self.curr_token)
            self.advanceT()
            self.compile_expression()
            self.eat(')')
            self.writeT(self.curr_token)
            self.advanceT()
        else:
            preToken = self.curr_token
            self.advanceT()
            if preToken[1] in CompilationEngine.unaryOp:
                self.writeT(preToken)
                self.compile_term()
            elif self.curr_token[1] == '[':
                self.writeT(preToken)  # name var
                self.writeT(self.curr_token)  # [
                self.advanceT()
                self.compile_expression()
                self.writeT(self.curr_token)  # ]
                self.advanceT()
            elif self.curr_token[1] == '.' or self.curr_token[1] == '(':  # sub call
                self.writeT(preToken)
                self.term_subroutineCall()
            else:
                self.writeT(preToken)  # var name\ const\ keyword
        self.writeLE("term")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.writeLS("expressionList")
        self.writeT(self.curr_token)
        self.advanceT()
        while self.curr_token[1] != ')':
            self.writeT(self.curr_token)
            self.advanceT()
            self.compile_expression()
        self.writeLE("expressionList")

    ##########

    def advanceT(self) -> None:
        self.tokenizer.advance()
        while not self.tokenizer.tokens:
            self.tokenizer.advance()
        self.curr_token = self.tokenizer.tokens[self.tokenizer.token_index]  # todo ######

    def eat(self, exp_token):
        if self.curr_token[1] != exp_token:  ####?????? curr token? לא משתנה ]1
            raise ValueError("MY ERROR" + exp_token + " " + self.curr_token[1])

    def writeLS(self, label) -> None:
        self.output_XML.write(" " * self.tab_num + "<" + label + ">\n")
        self.tab_num = +1

    def writeLE(self, label) -> None:
        self.tab_num = -1
        self.output_XML.write(" " * self.tab_num + "</" + label + ">\n")

    def writeT(self, token):  ###########
        self.output_XML.write(
            " " * self.tab_num + "<" + token[0] + ">" + token[1] + "</" + token[0] + "> \n")  ####??????? tuple

    def open_close_brackets_class(self):
        self.eat('{')
        self.writeT(self.curr_token)
        self.advanceT()
        while self.curr_token[1] in ['ststic', 'field']:
            self.compile_class_var_dec()
        while self.curr_token[1] in ['constructor', 'function', 'method']:
            self.compile_subroutine()
        self.eat('}')
        self.writeT(self.curr_token)

    def compile_statement(self):
        if self.curr_token[1] == "let":
            self.compile_let()
        if self.curr_token[1] == "if":
            self.compile_if()
        if self.curr_token[1] == "while":
            self.compile_while()
        if self.curr_token[1] == "do":
            self.compile_do()
        if self.curr_token[1] == "return":
            self.compile_return()

    def line_end(self):
        self.eat(';')
        self.writeT(self.curr_token)
        self.advanceT()

    def do_subroutineCall(self):
        self.writeT(self.curr_token)  # - var/class name  / subname
        self.advanceT()
        if self.curr_token[1] == '.':
            self.writeT(self.curr_token)  # .
            self.advanceT()
            self.writeT(self.curr_token)  # SUBname() -subroutin call todo
            self.advanceT()
        self.eat('(')
        self.writeT(self.curr_token)  # (
        self.advanceT()
        self.compile_expression_list()
        self.eat(')')
        self.writeT(self.curr_token)  # )
        self.advanceT()

    def term_subroutineCall(self):
        if self.curr_token[1] == '.':
            self.writeT(self.curr_token)  # .
            self.advanceT()
            self.writeT(self.curr_token)  # SUBname() -subroutin call todo
            self.advanceT()
        self.eat('(')
        self.writeT(self.curr_token)  # (
        self.advanceT()
        self.compile_expression_list()
        self.eat(')')
        self.writeT(self.curr_token)  # )
        self.advanceT()
