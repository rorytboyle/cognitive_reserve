import pandas as pd
from itertools import combinations

def create_unique_combinations(df, columns):
    """
    Creates a composite measure for every possible combination of
    cognitive reserve proxies. Credit to StackOverflow User WeNYoBenfor optimising my code and giving 
    a better solution https://stackoverflow.com/a/58895156/12384217

    :param df: pandas dataframe containing subject ids (as the index) and
                cognitive reserve data
    :param columns: List of strings containing column names for columns in data
                    containing cognitive reserve proxies.
    :return composites: dataframe with every possible unique combination of 'columns' in 'data'.
    """
    # Create unique combinations of each column, without repetition, based on column labels
    unique_combos = sum([list(map(list, combinations(df.columns, i)))
            for i in range(len(df.columns) + 1)], [])
    
    # Sum the columns in each unique combination and add to a new dataframe
    composites= pd.DataFrame(
            {'_'.join(x) : df[x].mean(axis=1) for x in unique_combos if x !=[]})
  

def test_unique_combinations(df, columns, composites):
    """
    Runs some basic tests to check composites were created as intended.

    :param df: pandas dataframe containing subject ids (as the index) and
                cognitive reserve data
    :param columns: List of strings containing column names for columns in data
                    containing cognitive reserve proxies.
    :param composites: df returned by create_unique_combinations(data, columns)
    :return cogResComposites: dataframe with every possible unique combination of 'columns' in 'data'.
    """
    # SANITY CHECK 1 - all column names in cogRes_composites should be unique
    comboNames = composites.columns.tolist()
    unique_elements_list = list(set(comboNames))
    errors = 0
    if len(comboNames) == len(unique_elements_list):
        print("Ok to proceed")
    else:
        print("STOP - CHECK DATA -  \nNot all column names in composite df (cogRes_composites) are unique")
        errors += 1

    # SANITY CHECK 2 - number of unique column names should equal number of 
    # possible combinations of proxies without repetition
    number_proxies = len(df.columns.tolist())
    
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
        errors += 1
        
    # SANITY CHECK 3 - check three random columns are actually combinations of
    # their respective underlying columns - e.g. check edu_occu is actually 
    # equal to the sum of edu and occu columns from original data 
    
    # get 5 random columns
    randomCols = composites.sample(5, axis=1).columns.tolist()
    
    for col in randomCols:
        underlyingCols = col.split("_")
        if composites[col].equals(
                composites[underlyingCols].sum(axis=1, skipna=False)):
            print("Ok to proceed")
        else:
            print("\nSTOP - CHECK DATA \n" + col + 
                  " not equal to the sum of \n" + ' + '.join(underlyingCols))
            errors += 1
    
    if errors == 0:
        print('Composites created fine - no problems identified')
    else:
        print('Error in creation of composites - please inspect data\n See above message for further info')
