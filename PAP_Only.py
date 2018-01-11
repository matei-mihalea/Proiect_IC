#size si pagesize-> in bytes (de asta se foloseste size - pagesize -> pagini complete)



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

##################################################### FUNCTII AUXILIARE ############################################
def MAXES(Holes):
	res = []
	for G in Holes:
		if G[1] not in res:
			res.append(G[1])
	return res

def HOLE_SATISFIED(size, G):#nu schimba valoarea argumentului?
	return [G[0], G[1] - size, G[2] + size]


def HOLE_FAILED_TO_SATISFY(size, G):
	new_val = G[1]
	if G[1] > size - pagesize:
		new_val = size - pagesize;
	return [G[0], new_val, G[2]]

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

def SORT_DESCENDING(maxes):
	res = []
	for max in maxes:
		for  m in max:
			res.append(m)

	return sorted(res, reverse=True)


def ALLOC(size):#presupunem ca alocarile vor merge de fiecare data
	return True

##################################################### FUNCTII DIN PSEUDOCOD ############################################
#imparte intervalul in parti (egale? -> nu sunt egale) de lungime split
#, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 48 and 64
def CALCULATE_STEPS(high, low, split):
	print(high, low)
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




##################################################### DECIDE #############################################################
def STATE_MAXES(s):#maximul pentru fiecare gaura in starea s
	maxes = []
	for max in MAXES(s):#MAXES = meximul pe fiecare gaura in starea s-> Gmax
		if max not in maxes:
			maxes.append(max)

	sorted_maxes = sorted(maxes, reverse=True)
	groups = GROUP_BY_MAX1(s, sorted_maxes)

	result = []
	for g in groups:
		result.append((random.choice(g), len(g)))
	return result


def DETERMINE_GROUPS(states):#maximul pentru toate starile
	maxes = []
	max_values = []
	for s in states:
		#maxes = maxes U STATE_MAXES(s)
		maxes.append(STATE_MAXES(s))

		for max in MAXES(s):
			if max not in max_values:
				max_values.append(max)#valorile maxime-> pentru group_by_max2

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


def DECIDE(states):
	print "DECIDE"
	maxvals = DETERMINE_GROUPS(states)

	(hole1, m) = maxvals[0]
	hmv = hole1[1]


	if hmv <= mshs:
		return states

	if len(maxvals) == 1:
		nhmv = mshs + pagesize
		if hmv == nhmv:
			return states
		sizes = CALCULATE_STEPS(hmv, nhmv, split)
		states = DESCEND(states, m, sizes)

	(hole2, m) = maxvals[1]
	nhmv = hole2[1]
	if nhmv <= mshs:
		nhmv = mshs + pagesize
	if hmv == nhmv:
		return states
	sizes = CALCULATE_STEPS(hmv, nhmv, split)
	print(states, m, sizes, hmv, nhmv)
	return DESCEND(states, m, sizes)



##################################################### DESCEND #############################################################
def ALLOCATE(m, size):#numara pentru cate din gauri reuseste alocarea
	count = 0
	for i in range(m):
		if ALLOC(size):
			count += 1
	return count

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


def UPDATE_STATES(states, size, count, m):
	nstates = []
	for s in states:
		candidates = []
		rest = []

		for G in s:
			if G[1] >= size:
				candidates.append(G)
			else:
				rest.append(G)

		if len(candidates) >= count:
			res = COMBINE(rest, count, candidates, size)
			nstates += res

	return nstates



def DESCEND(states, m, sizes):
	nstates = states
	print "DESCEND"
	print (len(states), states)
	for size in sizes:
		count = ALLOCATE(m, size)#cate alocari reusesc

		states = UPDATE_STATES(states, sizes[size], count, m)
		print(states, "states")
		if states == []:
			return nstates
		if count > 0:
			return DECIDE(states)



####################################################### MAIN ##########################################

def main(args):
	G1 = ["A", 1000000, 0]
	G2 = ["B", 999000, 0]
	G3 = ["C", 4996, 0]


	s1 = [G1, G2, G3]

	States = [s1]

	print 

	for max in STATE_MAXES(s1):
		print str(max[0]) + ", " +  str(max[1])
	print 

	#for maxval in DETERMINE_GROUPS(States):
	#	print maxval

	print DECIDE(States)



if __name__ == '__main__':
    main(sys.argv)