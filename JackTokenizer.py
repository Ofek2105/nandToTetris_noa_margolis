"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """
    KEYWORDS = {"class": "CLASS", "method": "METHOD", "function": "FUNCTION", "constructor": "CONSTRUCTOR",
                "int": "INT",
                "boolean": "BOOLEAN", "char": "CHAR", "void": "VOID", "var": "VAR", "static": "STATIC",
                "field": "FIELD",
                "let": "LET", "do": "DO", "if": "IF", "else": "ELSE", "while": "WHILE", "return": "RETURN",
                "true": "TRUE",
                "false": "FALSE", "null": "NULL", "this": "THIS"}
    SYMBOLS = {"(", ")", "{", "}", "[", "]", ",", ";", "=", ".", "+", "-", "*", "/", "&", "|", "~", "<", ">"}

    COMMENT_OPERATORS = ["//", "/*", "/**", "*/"]

    special_symbols_dict = {'>': '&gt;', '<': '&lt;', '"': '&quot;', '&': '&amp;'}

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.current_token = None
        self.input_lines = input_stream.read().splitlines()
        self.tokens = []
        self.curr_place = -1
        self.token_index = 0
        self.in_comment = False

    def remove_comments_spaces(self, line) -> str:
        """removes comments from input files"""

        line = line.replace("\t", "").strip()
        if "/**" in line or "/*" in line:
            self.in_comment = True
        if self.in_comment:
            if "*/" in line:
                self.in_comment = False
            return ""
        return line.split("//")[0]

    def split_line(self):
        index = 0
        cur_str = ""
        terms_lst = []
        this_line = self.input_lines[self.curr_place]
        this_line += " " if this_line and this_line[-1] != " " else ""

        while index < len(this_line):
            if this_line[index] in JackTokenizer.SYMBOLS:
                cur_str, index = self.check_and_append(cur_str, this_line[index], terms_lst, index + 1)
            elif this_line[index] == '"':
                term = this_line[index:this_line[index + 1:].find('"') + index + 2]
                cur_str, index = self.check_and_append(cur_str, term, terms_lst, index + len(term))
            elif this_line[index] == " ":
                cur_str, index = self.check_and_append(cur_str, "", terms_lst, index + 1)
            else:
                cur_str += this_line[index]
                index += 1

        return terms_lst

    def check_and_append(self, cur_str, term, terms_lst, new_index):
        if cur_str:
            terms_lst.append(cur_str)
        cur_str = ""
        terms_lst.append(term)
        return cur_str, new_index

    def tokenize_word(self, word):
        if word != "" or word != '':
            self.tokens.append(self.token_type(word))

    def read_line(self):
        """get the tokens from the line"""

        self.input_lines[self.curr_place] = self.remove_comments_spaces(self.input_lines[self.curr_place])
        for word in self.split_line():
            self.tokenize_word(word)

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.curr_place < len(self.input_lines) - 1

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        if self.curr_place == -1 or self.token_index == len(self.tokens):
            self.curr_place += 1
            self.read_line()
            self.token_index = 0
        else:
            self.token_index += 1
            if self.token_index == len(self.tokens):
                self.advance()

    def token_type(self, word):
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """

        if word in JackTokenizer.KEYWORDS:
            return 'keyword', word
        elif word in JackTokenizer.SYMBOLS:
            return 'symbol', word
        elif word in JackTokenizer.special_symbols_dict:
            return 'symbol', JackTokenizer.special_symbols_dict[word]
        elif word.isnumeric():
            return 'integerConstant', word
        elif word[0] == '"' and word[-1] == '"' and "\n" not in word[1:-1] and '"' not in word[1:-1]:
            return 'stringConstant', word
        elif (word[0].isalpha() or word[0] == "_") and word.replace("_", "").isalnum():
            return 'identifier', word
        else:
            return "ERROR", word

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return JackTokenizer.KEYWORDS[self.current_token]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self.current_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return str(self.current_token)

    def open_file(self, file):
        self.outfile = open(file.replace('.jack', 'T.xml'), 'w')
        self.outfile.write('<tokens>\n')

    def close_file(self):
        self.outfile.write('</tokens>')
        self.outfile.close()
