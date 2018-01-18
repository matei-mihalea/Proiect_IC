import sys

S = 1024
hole_size = 3000

def TEMP_ALLOC(size):#SUCCESS(1) daca poate fi a alocata memoria
	if size < S or size <= hole_size - S:
		return True
	else:
		return False

def DEDUCE(low, high):
	if low == high:
		return low

	if(high - low == 1):
		res = TEMP_ALLOC(high)
		if(res == 1):#SUCCESS
			return high
		else:
			return low

	mid_point = (high+low)/2;
	res = TEMP_ALLOC(mid_point);

	if res == True:
		return DEDUCE(mid_point, high)
	else:
		return DEDUCE(low, mid_point - 1)


def main(args):

	print(DEDUCE(1,2500))



if __name__ == '__main__':
    main(sys.argv)
