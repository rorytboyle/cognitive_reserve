import pandas as pd
import itertools
import math as math


def create_cogRes_composites(data, columns):
    """
    Standardises each cognitive reserve proxy score (i.e. z-scores) and
    then creates a composite measure for every possible combination of
    cognitive reserve proxies.

    :param data: pandas dataframe containing subject ids (as the index) and
                cognitive reserve data
    :param columns: List of strings containing column names for columns in data
                    containing cognitive reserve proxies.
    :return cogResComposites: dataframe with....
    """
    # select relevant cols
    data = data[columns]
    
    # standardise each proxy
    data = data.apply(lambda x: (x - x.mean()) / x.std(ddof=0))

    # Create composite scores - FIGURE OUT HOW TO ABSTRACT THIS FOR VARYING
    #                           LENGTH/AMOUNT OF PROXIES
    combos_2 = pd.DataFrame({'{}_{}'.format(a, b):
        data[a] + data[b] 
        for a, b in itertools.combinations(data.columns, 2)})
        
    combos_3 = pd.DataFrame({'{}_{}_{}'.format(a, b, c):
        data[a] + data[b] + data[c] 
        for a, b, c in itertools.combinations(data.columns, 3)})
        
    combos_4 = pd.DataFrame({'{}_{}_{}_{}'.format(a, b, c, d):
        data[a] + data[b] + data[c] + data[d] 
        for a, b, c, d
        in itertools.combinations(data.columns, 4)})
        
    combos_5 = pd.DataFrame({'{}_{}_{}_{}_{}'.format(a, b, c, d, e):
        data[a] + data[b] + data[c] + data[d] + data[e]
        for a, b, c, d, e in itertools.combinations(data.columns, 5)})
        
    combos_6 = pd.DataFrame({'{}_{}_{}_{}_{}_{}'.format(a, b, c, d, e, f):
        data[a] + data[b] + data[c] + data[d] + data[e] + data[f]
        for a, b, c, d, e, f in itertools.combinations(data.columns, 6)})
        
    combos_7 = pd.DataFrame({'{}_{}_{}_{}_{}_{}_{}'.format(a, b, c, d, e, f, g):
        data[a] + data[b] + data[c] + data[d] + data[e] + data[f] + data[g]
        for a, b, c, d, e, f, g in itertools.combinations(data.columns, 7)})
   
    cogRes_composites = pd.concat([data, combos_2, combos_3, combos_4, combos_5,
                                   combos_6, combos_7], axis=1)    

    # SANITY CHECK 1 - all column names in cogRes_composites should be unique
    comboNames = cogRes_composites.columns.tolist()
    unique_elements_list = list(set(comboNames))
    errors = 0
    if len(comboNames) == len(unique_elements_list):
        print("Ok to proceed")
    else:
        print("STOP - CHECK DATA -  \nNot all column names in composite df (cogRes_composites) are unique")
        errors += 1

    # SANITY CHECK 2 - number of unique column names should equal number of 
    # possible combinations of proxies without repetition
    number_proxies = len(data.columns.tolist())
    
    # calculate number of combos of n elements taken k in k
    def possibleCombos(n, k):
        combos = math.factorial(n) / (math.factorial(k) * math.factorial(n -k))
        return combos
    
    uniqueCombos = 0
    
    for i in range(1, number_proxies+1):
       uniqueCombos += possibleCombos(number_proxies, i)
       
    if uniqueCombos == len(unique_elements_list):
        print("Ok to proceed")
    else:
        print("STOP - CHECK DATA -  \nNumber of unique columns not equal to the number of unique combinations")
        s += 1
        
    # SANITY CHECK 3 - check three random columns are actually combinations of
    # their respective underlying columns - e.g. check edu_occu is actually 
    # equal to the sum of edu and occu columns from original data 
    
    # get 5 random columns
    randomCols = cogRes_composites.sample(5, axis=1).columns.tolist()
    
    for col in randomCols:
        underlyingCols = col.split("_")
        if cogRes_composites[col].equals(
                cogRes_composites[underlyingCols].sum(axis=1, skipna=False)):
            print("Ok to proceed")
        else:
            print("\nSTOP - CHECK DATA \n" + col + 
                  " not equal to the sum of \n" + ' + '.join(underlyingCols))
            errors += 1
    
    if errors == 0:
        return cogRes_composites
    else:
        print('No data returned because of error - please inspect data')
    