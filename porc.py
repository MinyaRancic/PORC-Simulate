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
def nop(state, noArg):
	return state

#offset can be a reg or an immediate
def jmp(state, offset):
	offsetNum = getNum(state, offest)
	state.readIdx += offsetNum
	return state

def latch_num_ascii(state, destReg):
	state.regs[int(destReg[1:])] = int(re.search("(\d+)", state.bytestream[state.readIdx:])
	return state

#numBytes can be a reg or an immediate
def latch_num_bin(state, (destReg, numBytes)):
	reg = int(destReg[1:])
	bytes = getNum(state, numBytes)
	int.from_byte(state.bytestream[state.readIdx:state.readIdx+bytes], "big")
	return state

def call(state, subgraph):
	return state

def ret(state, subgraph):
	return state

def match_jmp(state):
	state.readIdx += state.matchLength
	return state

#op1 and op2 may be immediates or registers
def add_sub(state, (op, destReg, op1, op2)):
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
	return false

def comp(state, (type, compReg, immediate)):
	num1 = getNum(state, compReg)
	num2 = getNum(state, immediate)
	if type == 0:
		return num1 < num2
	elif type == 1:
		return num2 > num1
	elif type == 2:
		return num1 == num2
	return false

def trueCond(state, arg):
	return true


class State():
	def __init__(self, numReg=32):
		self.regs = [0]*numReg
		# recall the default state is 'main'
		# a real compiler could map these to integer value states (e.g. main = 0, ...), but python makes it easy to do this
		self.currState = 'main'
		self.readIdx = 0
		self.bytestream = ""
		self.matchLength = 0

class Node():
	def __init__(self, name):
		self.transitions = []

	def addTransition(self, dest, condFunc, condArgs, actFunc, actArgs):
		self.transitions.append((dest, condFunc, condArgs, actFunc, actArgs))

#TODO: subgraph parsing
def parse(program):
	# construct state machine
	f = open(program, "r")
	nodeMap= {}
	for line in f:
		#each line is one transition - each for loop iteration builds one transition
		lineArr = line.split(' ')
		# construct the node if not seen before
		if line[0] not in nodeMap:
			nodeMap[line[0]] = Node(line[0])
		if line[1] not in nodeMap:
			nodeMap[line[1]] = Node(line[1])
		node = nodeMap[line[0]]
		dest = nodeMap[line[1]]
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
			condArgs = (condArr[1])
		elif condArr[0] == 'true':
			condFunc = trueCond
			condArgs = None
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






parse("test.porc")