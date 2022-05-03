from itertools import combinations
import math

'''
    Using the adapted formula from Gleiph's thesis
'''

'''
    How many ways are there to pick k elements from a set of n elements?
'''
def get_combinations_number(n, k):
    if n != 0 and k!=0:
        return math.factorial(n)/(math.factorial(k)*math.factorial((n - k)))
    else:
        return 1

'''
    How many ways are there to rearrange k elements from a set of n elements?
'''
def get_permutation_number(k, n):
    result = 0
    # try:
    result = math.factorial(n)/math.factorial(n-k)
    # except OverflowError:
        # result = math.factorial(n)//math.factorial(n-k)
    # finally:
    return result

'''
    Equation 1 in the SBES paper
'''
def combinations_no_restrictions(loc1, loc2):
    n = loc1 + loc2
    result = 0
    for i in range(1, n+1):
        result+=get_permutation_number(i, n)
    if loc1 == 0 or loc2 == 0:
        result = result - 1 # in this case, is only possible to exist v1, or v2, or v1v2, or v2v1
    else:
        result = result - 4 # excludes v1, v2, v1v2, and v2v1
    return int(result)

'''
    Equation 2 in the SBES paper
'''
def combinations_partial_order(loc1, loc2):
    result = 0
    for i in range(0,loc1+1):
        for j in range(0, loc2+1):
            result+=get_combinations_number(loc1, i) * get_combinations_number(loc2, j) * get_combinations_number(i+j, i) * min(1, i+j)
    if loc1 == 0 or loc2 == 0:
        result = result - 1 # in this case, is only possible to exist v1, or v2, or v1v2, or v2v1
    else:
        result = result - 4 # excludes v1, v2, v1v2, and v2v1
    return int(result)

'''
    Equation 3 in the SBES paper
'''
def combinations_partial_order_no_alternation(loc1, loc2):
    result = 0
    for i in range(0,loc1+1):
        for j in range(0, loc2+1):
            result+=get_combinations_number(loc1, i) * get_combinations_number(loc2, j) * (min(1, i) + min(1,j))
    if loc1 == 0 or loc2 == 0:
        result = result - 1 # in this case, is only possible to exist v1, or v2, or v1v2, or v2v1
    else:
        result = result - 4 # excludes v1, v2, v1v2, and v2v1
    return int(result)

def print_reduction_matrix_equation2():
    v1_max = 10
    v1_min = 0
    v2_max = 10
    v2_min = 0
    for v1_size in range(v1_min, v1_max+1):
        for v2_size in range(v2_min, v2_max+1):
            if v1_size == 0 and v2_size == 0:
                ratio = 0
            else:
                equation1_result = combinations_no_restrictions(v1_size, v2_size)
                equation2_result = combinations_partial_order(v1_size, v2_size)
                if equation1_result != 0 and equation2_result != 0:
                    ratio = (equation2_result/equation1_result)
                else:
                    ratio = 1
                
            
            if v1_size == 0 and v2_size == 0:
                print(f'N/A', end=' ')
            else:
                # print(f'{ratio*100:.3f} ({ratio})', end=' ')
                if ratio*100 < 0.001:
                    print(f'<0.001%', end=' ')
                else:
                    print(f'{ratio*100:.3f}%', end=' ')
                    
        print()

def print_reduction_matrix_equation3():
    v1_max = 10
    v1_min = 0
    v2_max = 10
    v2_min = 0
    for v1_size in range(v1_min, v1_max+1):
        for v2_size in range(v2_min, v2_max+1):
            if v1_size == 0 and v2_size == 0:
                ratio = 0
            else:
                equation1_result = combinations_partial_order(v1_size, v2_size)
                equation2_result = combinations_partial_order_no_alternation(v1_size, v2_size)
                if equation1_result != 0 and equation2_result != 0:
                    ratio = (equation2_result/equation1_result)
                else:
                    ratio = 1
                
            
            if v1_size == 0 and v2_size == 0:
                print(f'N/A', end=' ')
            else:
                # print(f'{ratio*100:.3f} ({ratio})', end=' ')
                if ratio*100 < 0.001:
                    print(f'<0.001%', end=' ')
                else:
                    print(f'{ratio*100:.3f}%', end=' ')
                    
        print()


if __name__ == '__main__':
    loc1 = 1
    loc2 = 0
    print(f'V1: {loc1} \t V2: {loc2}')
    result = combinations_no_restrictions(loc1, loc2)
    print(f'No restrictions: {result} options')

    result = combinations_partial_order(loc1, loc2)
    print(f'Respecting the partial order: {result} options')

    result = combinations_partial_order_no_alternation(loc1, loc2)
    print(f'Respecting the partial order and without alternation: {result} options')
    # print(get_combinations_number(3,2))
    print_reduction_matrix_equation2()