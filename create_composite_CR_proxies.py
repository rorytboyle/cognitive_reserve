# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 15:03:30 2019

@author: BOYLER1
"""

import pandas as pd
from scipy.stats import zscore
import itertools
import math as math

cogRes_raw = pd.read_csv(r'C:\Users\boyler1\Documents\PhD\CognitiveReserve\CognitiveReserve_validatedProxy\random_cog_res_data.csv')

cogRes_raw.set_index('subid', inplace=True)

################################# Z-Score Data ################################

# z-score each cognitive reserve indicator
cogRes = cogRes_raw.apply(zscore)

# Sanity Check zscore worked
zScore_sanityCheck =  (cogRes_raw['edu'] - cogRes_raw['edu'].mean()) / cogRes_raw['edu'].std(ddof=0)
zScore_sanityCheck = zScore_sanityCheck.round(6)
cogRes['edu'] == zScore_sanityCheck

#### fix above SLIGHTLY OFF ????


############################## Flip Directions ################################

# Flip directions - all values indicating higher cognitive reserve
cogRes['occu'] = cogRes['occu'] * -1

########################## Create Composite Scores ############################
combos_2 = pd.DataFrame({'{}_{}'.format(a, b):
    cogRes[a] + cogRes[b] 
    for a, b in itertools.combinations(cogRes.columns, 2)})
    
combos_3 = pd.DataFrame({'{}_{}_{}'.format(a, b, c):
    cogRes[a] + cogRes[b] + cogRes[c] 
    for a, b, c in itertools.combinations(cogRes.columns, 3)})
    
combos_4 = pd.DataFrame({'{}_{}_{}_{}'.format(a, b, c, d):
    cogRes[a] + cogRes[b] + cogRes[c] + cogRes[d] 
    for a, b, c, d
    in itertools.combinations(cogRes.columns, 4)})
    
combos_5 = pd.DataFrame({'{}_{}_{}_{}_{}'.format(a, b, c, d, e):
    cogRes[a] + cogRes[b] + cogRes[c] + cogRes[d] + cogRes[e]
    for a, b, c, d, e in itertools.combinations(cogRes.columns, 5)})
    
combos_6 = pd.DataFrame({'{}_{}_{}_{}_{}_{}'.format(a, b, c, d, e, f):
    cogRes[a] + cogRes[b] + cogRes[c] + cogRes[d] + cogRes[e] + cogRes[f]
    for a, b, c, d, e, f in itertools.combinations(cogRes.columns, 6)})
    
combos_7 = pd.DataFrame({'{}_{}_{}_{}_{}_{}_{}'.format(a, b, c, d, e, f, g):
    cogRes[a] + cogRes[b] + cogRes[c] + cogRes[d] + cogRes[e] + cogRes[f] + cogRes[g]
    for a, b, c, d, e, f, g in itertools.combinations(cogRes.columns, 7)})
   
cogRes_composites = pd.concat([cogRes, combos_2, combos_3, combos_4, combos_5,
                               combos_6, combos_7], axis=1)    

############################## Sanity Check 1 #################################
# check all column names in cogRes_composites are unique
comboNames = cogRes_composites.columns.tolist()
unique_elements_list = list(set(comboNames))

if len(comboNames) == len(unique_elements_list):
    print("Ok to proceed")
else:
    print("STOP - CHECK DATA -  \nNot all column names in composite df (cogRes_composites) are unique")    

############################## Sanity Check 2 #################################
# check number unique column names == number of unique possible combos without repetition
number_proxies = len(cogRes_raw.columns.tolist())

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

############################## Sanity Check 3 #################################
# check three random columns are actually combinations of their respective underlying columns
# e.g. check edu_occu is actually equal to cogRes['edu'] + cogRes['occu']  
    
# get 3 random columns
randomCols = cogRes_composites.sample(3, axis=1).columns.tolist()

for col in randomCols:
    underlyingCols = col.split("_")
    if cogRes_composites[col].equals(cogRes_composites[underlyingCols].sum(axis=1)):
        print("Ok to proceed")
    else:
        print("STOP - CHECK DATA \n" + col + " not equal to the sum of \n" + ' + '.join(underlyingCols))