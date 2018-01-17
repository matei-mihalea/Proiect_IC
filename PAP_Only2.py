#afla dimensiunea gaurilor -> stii ca informatia ascunsa este in A
#fiecare gaura are un max egal la inceput + stim dimensiunile reale(funcia de alocare va lua valori in functie de aceste valori)
#4 gauri -> large, small, B, C



#Real size
#Hole Total Max
#A 		0B 	1000GB
#B 		0B 	999GB
#C 		0B 	4.996GB

import sys
import random
from operator import itemgetter



S = 500000#la jumatatea gaurii A 
split = 20
pagesize = 1#MB
mshs = 50#MB



NAME = 0
MAX = 1
TOTAL = 2
SIZE = 3

############################################## FUNCTII PSEUDOCOD ############################################
def HOLE_SATISFIED(size, G):#nu schimba valoarea argumentului?
	return [G[NAME], G[MAX] - size, G[TOTAL] + size, G[SIZE]]


def HOLE_FAILED_TO_SATISFY(size, G):
	new_val = G[MAX]
	if G[MAX] > size:
		new_val = size
	return [G[NAME], new_val, G[TOTAL], G[SIZE]]


def MAXES(state):
	maxes = []
	for G in state:#MAXES = meximul pe fiecare gaura in starea s-> Gmax
		if G[MAX] not in maxes:
			maxes.append(G[MAX])

	return maxes


def STATE_MAXES(state):#maximul pentru fiecare gaura in starea s
	maxes = MAXES(state)
	sorted_maxes = sorted(maxes, reverse=True)
	groups = GROUP_BY_MAX1(state, sorted_maxes)

	result = []
	for g in groups:
		result.append((random.choice(g), len(g)))
	return result


def GROUP_BY_MAX1(Holes, maxes):#daca sunt 2 gauri cu acelasi max -> acelasi grup
	res = []
	for max in maxes:
		res.append([])

	for max in maxes:
		for G in Holes:
			if G[1] == max:
				res[maxes.index(max)].append(G)

	return res


def GROUP_BY_MAX2(States, maxes):#daca sunt 2 gauri cu acelasi max -> acelasi grup
	res = []
	for max in maxes:
		res.append([])

	for max in maxes:
		for state in States:
			for G in state:
				if G[0][1] == max:
					res[maxes.index(max)].append(G)

	return res


#imparte intervalul in parti (egale?) de lungime split
#, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 48 and 64
def CALCULATE_STEPS(high, low, split):
	size = high - low
	if size == pagesize:
		return [high]

	step = size / split
	sizes = {}#dictionar?
	idx = 0
	for n in range(split):
		sz = high - n * step
		rem = sz % pagesize

		if rem > 0:
			sz -= rem + pagesize
		if idx == 0 or sizes[idx - 1]  != sz:
			sizes[idx] = sz
			idx += 1

	return sizes



def DETERMINE_GROUPS(states):#maximul pentru toate starile
	maxes = []
	max_values = []
	for s in states:
		#maxes = maxes U STATE_MAXES(s)
		maxes.append(STATE_MAXES(s))

		for max in MAXES(s):
			if max not in max_values:
				max_values.append(max)#valorile maxime-> pentru group_by_max2

	print maxes
	if len(maxes) > 1:
		maxes = sorted(maxes, key=itemgetter(1), reverse=True)
	max_values = sorted(max_values, reverse=True)
	groups = GROUP_BY_MAX2(maxes, max_values)

	result = []
	for g in groups:
		#g = SORT-DESCENDING-BY-MULTIPLICITY(g)
		g = sorted(g, key=itemgetter(1), reverse=True)
		maxval = g[0]
		result.append(maxval)


	return result


def NSTATE(size, rest, satisfied, not_satisfied):

	holes = rest
	for G in satisfied:
		holes.append(HOLE_SATISFIED(size, G))
	for G in not_satisfied:
		holes.append(HOLE_NOT_SATISFIED(size, G))
	return holes#CREATE_STATE(holes)


def DO_COMBINE(rest, selected, previous, count, candidates, accum, size):#added argument size

	if count == 0:
		nstate = NSTATE(size, rest, selected, previous)
		accum.append(nstate)
		return accum
	elif len(candidates) == 0:
		return accum
	else:
		x = candidates[0]
		candidates = candidates[1:]#candidates = TAIL(candidates)


		sel = selected
		sel.append(x)
		l = DO_COMBINE(rest, sel, previous, count - 1, candidates, accum, size)
		accum += l
		prev = previous
		prev.append(x)
		return DO_COMBINE(rest, selected, prev, count, candidates, accum, size)

def COMBINE(rest, count, candidates, size):#added argument size
	return DO_COMBINE(rest, [], [], count,candidates, [], size)


############################################## FUNCTII PROPRII #######################################
def ALLOCATE(G, size):
	#G[SIZE] - G[TOTAL] -> cat a ramas nealocat din gaura respectiva
	if G[SIZE] - G[TOTAL] > size:
		return True
	return False


def UPDATE_STATES(state, Holes):
	for G in Holes:
		for G1 in state:
			if G1[NAME] == G[NAME]:
				state.remove(G1)
				state.append(G)
				break

def HALVE_MAXES(state):
	res = []
	for G in state:
		G[MAX] /= 2
		res.append(G)

	state = res

def CHECK_DONE(state):
	for G in state:
		if G[MAX] > 1:
			return False
	return True


#recursive/iterative?
#se incepe de la o stare unica -> DESCENT
def DESCEND(G, sizes):

	for index in reversed(list(sizes)):
		size = sizes[index]

		if ALLOCATE(G,size) == True:#incearca alocarea 
			return (HOLE_SATISFIED(size, G), "Allocation success")
		else:
			G = HOLE_FAILED_TO_SATISFY(size, G)

	#no allocation succeeded
	return (G, "All allocation sizes failed")


def FORK(Holes, sizes):
	res = []

	#allocate Holes
	for index in reversed(list(sizes)):
		size = sizes[index]

		count = 0

		new_vals = []
		for G in Holes:
			if ALLOCATE(G,size) == True:#incearca alocarea 
				G = HOLE_SATISFIED(size, G)
				count += 1
			else:
				G = HOLE_FAILED_TO_SATISFY(size, G)
			new_vals.append(G)


		if count == len(Holes):
			UPDATE_STATES(Holes, new_vals)
			return (Holes, "All success")
		elif count > 0:
			# fork multiple states
			UPDATE_STATES(Holes, new_vals)
			return (Holes, "Partial success")


		#count == 0
		UPDATE_STATES(Holes, new_vals)
		
	return (Holes, "All allocation sizes failed for all holes")


def PAP(state):
	state_maxes = STATE_MAXES(state)

	if CHECK_DONE(state):
		final_state = []
		for G in state:
			final_state.append([G[NAME], G[MAX] - 1, G[TOTAL] + 1, G[SIZE]])
		print final_state
		return

	if state_maxes[0][1] == 1:#hmv unic(DESCENT MODE)
		hmv = state_maxes[0][0][MAX]
		nhmv = state_maxes[1][0][MAX]

		sizes = CALCULATE_STEPS(nhmv, hmv, split)
		
		(G, message) = DESCEND(state_maxes[0][0], sizes)


		UPDATE_STATES(state, [G])
		PAP(state)

	else:#hmv has muliplicity m(FORK MODE)

		hmv = state_maxes[0][0][MAX]
		if state_maxes[0][1] != len(state):
			nhmv = state_maxes[1][0][MAX]
		else:
			nhmv = hmv / 2

		maxes = MAXES(state)
		sorted_maxes = sorted(maxes, reverse=True)
		groups = GROUP_BY_MAX1(state, sorted_maxes)

		sizes = CALCULATE_STEPS(nhmv, hmv, split)
		(Holes, message) = FORK(groups[0], sizes)

		UPDATE_STATES(state, Holes)
		if message == "All success" or message == "Partial success":
			pass

		PAP(state)

######################################################################################################

def main(args):
	
	#Initializations
	A_size = 1000000

	#large_size + small_size = A_size
	small_size = 200000
	large_size = 800000
	B_size = 999000
	C_size = 4996


	#max = dublu max(A) real la inceput -> presupuse
	G1 = ["large", 2400000, 0, large_size]
	G2 = ["small", 2300000, 0, small_size]
	G3 = ["B", 2200000, 0, B_size]
	G4 = ["C", 2100000, 0, C_size]


	s1 = [G1, G2, G3, G4]
	States = [s1]

	#Debug & Print Functions
	#print "Initial state"
	#for s in States:
	#	print s[NAME]
	#	print s[MAX]
	#	print s[TOTAL]
	#print 

	#print "State maxes"

	#for max in STATE_MAXES(s1):
	#	print str(max[NAME]) + ", " +  str(max[MAX])
	#print 

	#print "Calculate steps"
	#sizes = CALCULATE_STEPS(0, G1[MAX], split)
	#print sizes
	#print

	#print "Determine groups"
	#print DETERMINE_GROUPS(States)
	#print







	#PAP Algorithm -> se va termina cand toate gaurile sunt alocate(max = 0 -> total va fi realsize-ul) sau cand gaseste dimensiunea L(cea mai mare gaura)
	PAP(s1)


if __name__ == '__main__':
    main(sys.argv)