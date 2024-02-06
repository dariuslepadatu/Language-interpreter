# Language-interpreter

This project is an interpreter for lambda expressions, concatenations, and sums.
Given an input string, it constructs a Non-Deterministic Finite Automaton (NFA) and then converts it into a Deterministic Finite Automaton (DFA) in the lexer.

# Code Structure
The code consists of two main parts:

Node Class: This class represents nodes of the abstract syntax tree (AST) for lambda expressions. It defines various methods for processing and evaluating lambda expressions, such as resolving lambda closures, replacing arguments in lambda functions, solving lambda functions, and more.

Main Function: The main function serves as the entry point of the program. It uses a lexer to tokenize the input lambda expression and constructs an AST by parsing the tokens. It then performs various transformations on the AST to evaluate the lambda expression and print the result.

Usage
To use the Lambda Expression Interpreter, provide an input lambda expression as a command-line argument when running the program. The program will tokenize the input, parse it into an AST, and evaluate the expression, printing the result.

Example command to run the program:

bash
Copy code
python interpreter.py "((lambda x: lambda x: x 1) 2)"
Supported Lambda Expression Features
The interpreter supports the following features in lambda expressions:

Lambda functions defined with lambda.
Variable names containing lowercase letters [a-z].
Lambda function application using parentheses (lambda ...).
Concatenation using ++.
Summation using +.
Numeric values [0-9]+.
Limitations
The interpreter has some limitations and assumptions:

It assumes that the input lambda expression is well-formed and syntactically correct.
It supports single-letter variable names with optional numerical suffixes to distinguish variables with the same name.
It may not handle complex lambda expressions or error cases.
Example
For the input expression ((lambda x: lambda x: x 1) 2), the interpreter will evaluate it to 3 as a result.

Please note that this is a simplified interpreter and may require further enhancements for handling more complex expressions or additional features.
