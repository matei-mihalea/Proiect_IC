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
import itertools
from copy import deepcopy, copy



S = 500000#la jumatatea gaurii A 
split = 24
pagesize = 1#MB
mshs = 50#MB



NAME = 0
MAX = 1
TOTAL = 2
SIZE = 3

############################################## FUNCTII PSEUDOCOD ############################################
def HOLE_SATISFIED(size, G):#nu schimba valoarea argumentului?
	if G[MAX] - size >= 0:
		new_val = G[MAX] - size
	else:
		new_val = 0
	return [G[NAME], new_val, G[TOTAL] + size, G[SIZE]]


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


def CHECK_STATE(state):
	for G in state:
		if G[TOTAL] > G[SIZE]:
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
			#print G

	#no allocation succeeded
	return (G, "All allocation sizes failed")


def FORK(Holes, sizes):
	res = []

	#allocate Holes
	for index in reversed(list(sizes)):
		size = sizes[index]

		count = 0

		#prima data vezi cate alocari reuses
		for G in Holes:
			if ALLOCATE(G,size) == True:#incearca alocarea 
				count += 1


		if count == len(Holes):
			new_vals = []
			for G in Holes:
				G = HOLE_SATISFIED(size, G)
				new_vals.append(G)
			UPDATE_STATES(Holes, new_vals)
			return ([Holes], "All success")
		elif count > 0:
			# fork multiple states

			rez = []
			for combinations in itertools.combinations(Holes, count):

				new_vals = []
				CHoles = copy(Holes)
				for G in Holes:
					if G in combinations:
						G = HOLE_SATISFIED(size, G)
					else:
						G = HOLE_FAILED_TO_SATISFY(size, G)
					new_vals.append(G)

				UPDATE_STATES(CHoles, new_vals)
				rez.append(CHoles)


			return (rez, "Partial success")


		new_vals = []
		for G in Holes:
			G = HOLE_FAILED_TO_SATISFY(size, G)
			new_vals.append(G)
		UPDATE_STATES(Holes, new_vals)

	return ([Holes], "All allocation sizes failed for all holes")


def PAP(state):
	state_maxes = STATE_MAXES(state)

	if CHECK_DONE(state):
		final_state = []
		for G in state:
			final_state.append([G[NAME], G[MAX] - 1, G[TOTAL] + 1, G[SIZE]])
		all_final_states.append(final_state)
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
		(new_hole_vals, message) = FORK(groups[0], sizes)#returneaza mai multe stari(posibil)

		for Holes in new_hole_vals: 
			cstate = copy(state)
			UPDATE_STATES(cstate, Holes)
			#print Holes
			if message == "All success" or message == "Partial success":
				pass#return

			PAP(cstate)

######################################################################################################

def main(args):
	global all_final_states
	all_final_states = []
	
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
	print len(all_final_states)
	for state in all_final_states:
		if CHECK_STATE(state):
			print state


if __name__ == '__main__':
    main(sys.argv)