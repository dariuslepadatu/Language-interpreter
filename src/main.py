from sys import argv
from .Lexer import Lexer


class Node:
	value: any
	type: str
	children: any
	up : 'Node'

	def __init__(self, value, type):
		self.value = value
		self.type = type
		self.up = None
		self.children = []

	
	def __str__(self, level=0):
		result = "  " * level + f"{level}: {self.value}\n"

		for child in self.children:
				result += child.__str__(level + 1)

		return result
	

	# gets the value that replaces the argument of the lambda function
	def getValue(self) -> 'Node':
		if len(self.children) >= 2:
			for child in self.children:
				return child.getValue()
		if len(self.children) == 1:
			if self.up:
				return self.up.children[1]
			return None
		return None
	
	# returns first lambda function encountered
	def getLambda(self) -> 'Node':
		if 	self.type == 'LAMBDA':
			return self
		if self.type in ['L_PAR', 'SUM', 'APPEND']:
			for child in self.children:
				lambda_node = child.getLambda()
				if lambda_node is not None:
					return lambda_node
		return None
		

	# replaces all appearences of arg with new_node in lambda
	def replaceInLambda(self, arg, new_node) -> None:
		if self.type != 'LAMBDA':
			if arg == self.value:
				self.value = new_node.value
				self.type = new_node.type
				self.children = new_node.children
		for child in self.children:
			child.replaceInLambda(arg, new_node)

	# while there are lambda functions, it solves them and
	# updates the tree
	def solveLambda(self) -> 'Node':
		lambda_node = self.getLambda()
		while lambda_node:
		
			new_node = self.getValue()
			if new_node is None:
				new_node = lambda_node.up.getValue()

			if lambda_node.up:
				if lambda_node.up.up:
					# if the tree looks like this ( -> ( -> lambda x -> x,
					# the second bracket is deleted, the tree remaining ( -> x
					for child in lambda_node.children:
						child.up = lambda_node.up.up
					idx = 0
					for upChild in lambda_node.up.up.children:
						if upChild is lambda_node.up:
							break
						idx += 1

					lambda_node.up.up.children[idx] = lambda_node.children[0]
				else:
					# top of the tree
					self = lambda_node.children[0]
					self.up = None

			# deletes the value (used to replace arg in the lambda function) from the tree
			if new_node.up:
				new_node.up.children = [new_node.up.children[0]]

			arg = lambda_node.value.split(' ')[1]
			lambda_node.replaceInLambda(arg, new_node)

			lambda_node = self.getLambda()
		return self
	

	def getLevel(self) -> int:
		cont = 0
		node = self
		while node.up:
			node = node.up
			cont += 1
		return cont

	# finds the deepest sum or append function
	def deepestSumOrAppend(self) -> 'Node':
		deepest_node = None
		if self.type in ['SUM', 'APPEND']:
			deepest_node = self

		for child in self.children:
			child_result = child.deepestSumOrAppend()

			if child_result:
				# check if child node is deeper than the current node 
				if deepest_node is None or child_result.getLevel() > deepest_node.getLevel():
					deepest_node = child_result

		return deepest_node
		
	# returns the list containing all numbers from a node
	def solveAppend(self)-> list:
		value = []
		if self.type == 'NUMBER':
			return int(self.value)
		
		if self.type == 'L_PAR' and self.children == [] and self.up.up.type != 'APPEND':
			return str('NULL')

		for child in self.children:
			child_value = child.solveAppend()

			# if child is a list, extend current list with child's elements
			if isinstance(child_value, list):
				value.extend(child_value)
			else:
				value.append(child_value)

		return value

	def solveSum(self) -> int:
		value = 0
		if self.type =='NUMBER':
			value = int(self.value)
		for child in self.children:
			value += child.solveSum()
		return value 
	
	def solveSumAndAppend(self) -> 'Node':
		node = self.deepestSumOrAppend()
		while node:
			new_node = None
			if node.type == 'SUM':
				new_node = Node(node.solveSum(), 'NUMBER')
			if node.type == 'APPEND':

				list = node.solveAppend()
				new_node = Node('(', 'L_PAR')
				for elem in list:
					if elem == 'NULL':
						new_node.children.append(Node('(', 'L_PAR'))
					else:
						new_node.children.append(Node(elem, 'NUMBER'))
			
			if node.up:
				if node.up.up:
					for child in node.children:
						child.up = node.up.up
					node.up.up.children[0] = new_node
				else:
					# top of the tree
					self = new_node
					self.up = None
			node = self.deepestSumOrAppend()
		return self
	
	def getResult(self) -> str:
		result = ""
		if self.type == 'NUMBER':
			result += str(self.value)
		if self.type == 'L_PAR':
			result += '('
			if self.children != []:
				result += ' '
			for child in self.children:
				result +=  child.getResult() + ' '
			result += ')'
		return result

	def __str__(self, level=0):
		result = "  " * level + f"{level}: {self.value}\n"

		for child in self.children:
				result += child.__str__(level + 1)

		return result


def main():
	if len(argv) != 2:
		return
	
	spec = [
			("SPACE", "\\ "),
			("L_PAR", "("),
			("R_PAR", ")"),
			("LAMBDA", "lambda"),
			("VARIABLE", "[a-z]+"),
			("COLON", ":"),
			("APPEND", "++"),
			("SUM", "+"),
			("NUMBER", "[0-9]+")
		]
	

	lexer = Lexer(spec)

	filename = argv[1]
	
	content = ""
	with open(filename, 'r') as file:
		for line in file:
			content += line.strip()
			content += " "


	# content contains the entire content of the file as a string
	content = content.strip()
	lexemes = lexer.lex(content)

	root = None
	last_node = None
	parsingArg = False
	parseLambda = False
	usedVar = {}
	for type, value in lexemes:

		if type == 'SPACE':
			continue
		if root is None:
			root = Node(value, type)
			last_node = root
		else:
			new_node = Node(value, type)

			if type == 'LAMBDA' and parsingArg == False:
				parsingArg = True
				new_node.up = last_node
				last_node.children.append(new_node)
				last_node = new_node
			
			elif type == 'VARIABLE' and parsingArg:
				if value in usedVar:
					usedVar[value] += 1
				else:
					usedVar[value] = 0
				last_node.value += ' ' + value + str(usedVar[value])
				parsingArg = False
				parseLambda = True
			
			elif type == 'L_PAR':
				new_node.up = last_node
				last_node.children.append(new_node)
				last_node = new_node

			elif type == 'APPEND' or type == 'SUM':
				new_node.up = last_node
				last_node.children.append(new_node)
				last_node = new_node

			elif type == 'NUMBER' or type == 'VARIABLE':
				if type == 'VARIABLE':
					new_node.value = value + str(usedVar[value])
				if type == 'NUMBER' and parseLambda == True:
					while last_node:
						if '(' in last_node.value :
							break
						last_node = last_node.up	
				new_node.up = last_node
				last_node.children.append(new_node)

			# go up in tree when a bracket is closed to the first
			# bracket opened but not closed
			elif type == 'R_PAR':
				parseLambda = False
				cont = 0
				while last_node:
					if last_node.type == 'L_PAR':
						cont += 1
					if cont == 2:
						break
					last_node = last_node.up


	root = root.solveLambda()
	root = root.solveSumAndAppend()
	print(root.getResult())


if __name__ == '__main__':
    main()