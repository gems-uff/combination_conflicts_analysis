import math

'''
    Using the adapted formula from Gleiph's thesis
'''

'''
    How many ways are there to pick k elements from a set of n elements?
'''
def get_combinations_number(n, k):
    return math.factorial(n)/(math.factorial(k)*math.factorial((n - k)))

'''
    How many ways are there to rearrange k elements from a set of n elements?
'''
def get_permutation_number(k, n):
    return math.factorial(n)/math.factorial(n-k)

def combinations_no_restrictions(loc1, loc2):
    n = loc1 + loc2
    result = 0
    for i in range(1, n+1):
        result+=get_permutation_number(i, n)
    return int(result)

def combinations_partial_order(loc1, loc2):
    result = 0
    for i in range(0,loc1+1):
        for j in range(0, loc2+1):
            result+=get_combinations_number(loc1, i) * get_combinations_number(loc2, j) * get_combinations_number(i+j, i) * min(1, i+j)
    return int(result)

def combinations_partial_order_no_alternation(loc1, loc2):
    result = 0
    for i in range(0,loc1+1):
        for j in range(0, loc2+1):
            result+=get_combinations_number(loc1, i) * get_combinations_number(loc2, j) * (min(1, i) + min(1,j))
    return int(result)


if __name__ == '__main__':
    loc1 = 3
    loc2 = 7

    result = combinations_no_restrictions(loc1, loc2)
    print(f'No restrictions: {result} options')

    result = combinations_partial_order(loc1, loc2)
    print(f'Respecting the partial order: {result} options')

    result = combinations_partial_order_no_alternation(loc1, loc2)
    print(f'Respecting the partial order and without alternation: {result} options')