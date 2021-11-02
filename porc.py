# import numpy as np
import re

#helper, takes in an arg (reg or immediate) and returns the integer rep
def getNum(state, arg):
	if arg[0] == "#":
		return int(arg[1:])
	elif arg[0] == "r":
		return state.regs[int(arg[1:])]
	else:
		return None

# action functions: State -> Args -> State
def nop(state):
	return state

#offset can be a reg or an immediate
def jmp(state, offset):
	offsetNum = getNum(state, offset)
	state.readIdx += offsetNum
	return state

def latch_num_ascii(state, destReg):
	state.regs[int(destReg[1:])] = int(re.search("(\d+)", state.bytestream[state.readIdx:]).group(1))
	state.readIdx += state.regs[int(destReg[1:])]
	return state

#numBytes can be a reg or an immediate
def latch_num_bin(state, destReg, numBytes):
	reg = int(destReg[1:])
	bts = getNum(state, numBytes)
	state.regs[reg] = int.from_bytes(state.bytestream[state.readIdx:state.readIdx+bts].encode(), "big")
	state.readIdx += bts
	return state

def call(state, subgraph):
	return state

def ret(state, subgraph):
	return state

def match_jmp(state):
	state.readIdx += state.matchLength
	return state

#op1 and op2 may be immediates or registers
def add_sub(state, op, destReg, op1, op2):
	op1Num = getNum(state, op1)
	op2Num = getNum(state, op2)
	reg = int(destReg[1:])

	if op=="add":
		state.regs[reg] = op1Num + op2Num
	else:
		state.regs[reg] = op1Num - op2Num
	return state

# condition functions: State -> Args -> bool
def match(state, string):
	string = string.replace("\\r", "\r")
	string = string.replace("\\n", "\n")
	string = string[1:len(string)-1]
	print("checking for: " + string.replace("\r", "\\r").replace("\n", "\\n") + " " + str(state.readIdx) + " " + str(state.readIdx + len(string)))
	print(state.bytestream[state.readIdx:state.readIdx+len(string)].replace("\r", "\\r").replace("\n", "\\n"))
	state.matchLength = len(string)
	return state.bytestream[state.readIdx:state.readIdx+len(string)] == string

def comp(state, type, compReg, immediate):
	num1 = getNum(state, compReg)
	num2 = getNum(state, immediate)
	if type == 0:
		return num1 < num2
	elif type == 1:
		return num2 > num1
	elif type == 2:
		return num1 == num2
	return False

def trueCond(state, arg):
	return True


class State():
	def __init__(self, numReg=32):
		self.regs = [0]*numReg
		# recall the default state is 'main'
		# a real compiler could map these to integer value states (e.g. main = 0, ...), but python makes it easy to do this
		self.currState = 'main'
		self.readIdx = 0
		with open ("dnsHeader.test", "r") as myfile:
			self.bytestream = myfile.read()
		self.matchLength = 1

class Node():
	def __init__(self, name):
		self.transitions = []
		self.name = name

	def addTransition(self, dest, condFunc, condArgs, actFunc, actArgs):
		self.transitions.append((dest, condFunc, condArgs, actFunc, actArgs))

	def drive(self, state):
		print(self.name)
		for (dest, condFunc, condArgs, actFunc, actArgs) in self.transitions:
			if condFunc(state, *condArgs):
				return (dest, actFunc(state, *actArgs))
		state.readIdx += 1
		return (self, state)
	
	def getName(self):
		return self.name

#TODO: subgraph parsing
def parse(program):
	# construct state machine
	f = open(program, "r")
	nodeMap= {}
	for line in f:
		#each line is one transition - each for loop iteration builds one transition
		lineArr = line.split(' ')
		# construct the node if not seen before
		if lineArr[0] not in nodeMap:
			nodeMap[lineArr[0]] = Node(lineArr[0])
		if lineArr[1] not in nodeMap:
			nodeMap[lineArr[1]] = Node(lineArr[1])
		node = nodeMap[lineArr[0]]
		dest = nodeMap[lineArr[1]]
		#begin construction transition
		paren = re.findall('\(([^)]+)', line)
		condStr = paren[0]
		actStr = paren[1]

		#condStr is annoying, TODO
		condArr = condStr.split(' ')
		condFunc = None
		condArgs = None
		op = None
		if(condArr[0] == 'match'):
			condFunc = match
			condArgs = (condArr[1],)
		elif condArr[0] == 'true':
			condFunc = trueCond
			condArgs = (None,)
		else:
			condFunc = comp
			if condArr[1] == '<':
				op = 0
			elif condArr[1] == '>':
				op = 1
			elif condArr[2] == "==":
				op = 2
			else:
				op = 3
			condArgs = (op, condArr[0], condArr[2])
		print(str(condFunc) + " " + str(condArgs))
		#act str easy?
		actArr = actStr.split(' ')
		actFunc = eval(actArr[0]) #gives the func ptr
		actArgs = tuple(actArr[1:])
		print(str(actFunc) + " " + str(actArgs))

		node.addTransition(dest, condFunc, condArgs, actFunc, actArgs)
	print(nodeMap)
	return nodeMap


nodeMap = parse("dns_header.porc")
node = nodeMap['$main']
state = State()
prevIdx = 0
sizes = []
while state.readIdx < len(state.bytestream):
	print((state.readIdx, len(state.bytestream)))
	(node, state) = node.drive(state)
	if node.getName() == '$end':
		#implicit transition
		node = nodeMap['$main']
		sizes.append(state.readIdx - prevIdx)
		prevIdx = state.readIdx
if node.getName() == '$end':
		#implicit transition
		node = nodeMap['$main']
		sizes.append(state.readIdx - prevIdx)
		prevIdx = state.readIdx

print(state.readIdx)
print(state.regs)
print(sizes)