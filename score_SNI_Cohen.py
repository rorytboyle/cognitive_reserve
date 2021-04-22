def score_SNI_Cohen(df):
    """
    Scores the Social Network Index Questionnaire following the 
    instructions outlined in https://www.midss.org/sites/default/files/social_network_index_scoring.pdf

    Note: this function does not clean the data. Please ensure the data is
    cleaned before scoring with this function.Any missing values should be = 0.
    
    @author: Rory Boyle rorytboyle@gmail.com
    @date: 22/04/2021

    :param df: pandas dataframe (or .csv file) of size p * 35 (p = number of 
                participants). Index should be subid. Cols = 35 columns 
                containing responses to Social Network Index Questionnaire. 

    :return SNI_scored: dataframe with scored SNI data with following columns:
                    - Column 1 (subid)= participant id
                    - Column 2 (SNI_Roles) = number of high contact roles
                    - Column 3 (SNI_People) = number of people in social network
                    - Column 4 (SNI_Networks) = number of embedded networks
    """
    import pandas    
    import numpy
    
    # test
    df=sni.copy()
    
    #%% 1) Score Number of High-Contact Roles (Network Diversity)
    # for SNI_1 (spouse) only answers = 1 should be retained as 1
    spouse = df['SNI_1']
    spouse = spouse.where(spouse==1)
    spouse.replace(np.nan, 0, inplace=True)
    
    # get other answers for network diversity
    net_div = df[['SNI_2a', 'SNI_3a', 'SNI_4a', 'SNI_5a', 'SNI_6a', 'SNI_7a',
                  'SNI_8a', 'SNI_9a', 'SNI_9b', 'SNI_10', 'SNI_11', 'SNI_12']]
    
    # replace all non zeros with 1
    net_div.replace(np.nan, 0, inplace=True)    
    net_div[net_div != 0] = 1
    
    # for employee both 9a and 9b must = 1 to be scored as 1 overall
    employee = net_div[['SNI_9a', 'SNI_9b']].sum(axis=1)
    employee.replace(1, 0, inplace=True)
    
    # drop employee qs from other answers
    net_div.drop(['SNI_9a', 'SNI_9b'], axis=1, inplace=True)
    
    # add back spouse and employee answers
    net_div['SNI_1'] = spouse
    net_div['SNI_9'] = employee
    
    #sum for total 
    num_high_contact = net_div.sum(axis=1)
    
    #%% 2) Score Number of People in Social Network
    # get answers where simple sum of numbers used
    num_people = df[['SNI_2a', 'SNI_5a', 'SNI_6a', 'SNI_7a', 'SNI_8a', 'SNI_9a',
                     'SNI_9b', 'SNI_10', 'SNI_11a', 'SNI_12a_number', 
                     'SNI_12b_number', 'SNI_12c_number', 'SNI_12d_number',
                     'SNI_12e_number', 'SNI_12f_number']]
    
    # add spouse where answer = 1 if married
    num_people['SNI_1'] = spouse
    
    # replace answers for speaking to parents + parent in laws 3a, 4a
    parents_inlaws = df[['SNI_3a', 'SNI_4a']]
    parents_inlaws.replace([1, 2, 3], [1, 1, 2], inplace=True)
    
    num_people[['SNI_3a', 'SNI_4a']] = parents_inlaws[['SNI_3a', 'SNI_4a']]
    
    num_people.replace(np.nan, 0, inplace=True)
    
    # sum for total
    num_people = num_people.sum(axis=1)
    
    #%% 3) Score Number of Embedded Networks
    # get answers for easily scored ntwrks (friends, church, school,
    # neighbours, volunteers)
    ntwrks = df[['SNI_6a', 'SNI_7a', 'SNI_8a', 'SNI_10', 'SNI_11a']]
    
    # assign score of 1 to networks w/ >= 4 high contact people
    ntwrks[ntwrks < 4] = 0
    ntwrks[ntwrks >= 4] = 1
    
    # get score for work networks
    work_ntwrk = df[['SNI_9a', 'SNI_9b']].sum(axis=1)
    work_ntwrk[work_ntwrk < 4] = 0
    work_ntwrk[work_ntwrk >= 4] = 1
    ntwrks['SNI_9'] = work_ntwrk
    
    # get score for group networks    
    groups_ntwrk = df[['SNI_12a_number', 'SNI_12b_number', 'SNI_12c_number',
                       'SNI_12d_number', 'SNI_12e_number', 'SNI_12f_number']].sum(axis=1)
    groups_ntwrk[groups_ntwrk < 4] = 0
    groups_ntwrk[groups_ntwrk >= 4] = 1
    ntwrks['SNI_12'] = groups_ntwrk
    
    # get score for family networks
    
    # count number of high-contact family roles
    family_roles = df[['SNI_2a', 'SNI_3a', 'SNI_4a', 'SNI_5a']]
    family_roles['SNI_1'] = spouse
    family_roles.replace(0, np.nan, inplace=True)
    family_roles = family_roles.count(axis=1)
    
    # assign 0.5 if at least 3 high-contact family roles
    family_roles[family_roles < 3] = 0
    family_roles[family_roles >= 3] = 0.5
    
    # count number of family members
    family_members = df[['SNI_2a', 'SNI_3a', 'SNI_4a', 'SNI_5a']]
    family_members['SNI_1'] = spouse
    family_members = family_members.sum(axis=1)
    
    # assign 0.5 if at least 4 high-contact family members
    family_members[family_members < 4] = 0
    family_members[family_members >= 4] = 0.5
    
    family_ntwrk = family_roles + family_members
    family_ntwrk.replace(0.5, 0, inplace=True)
    
    ntwrks['family'] = family_ntwrk

    # sum embedded networks
    ntwrks.replace(np.nan, 0, inplace=True)
    num_ntwrks = ntwrks.sum(axis=1) 
    
    #%% 4) Merge three scores and return
    sni_scored = pd.DataFrame(index=df.index)
    
    sni_scored['SNI_Roles'] = num_high_contact
    sni_scored['SNI_People'] = num_people 
    sni_scored['SNI_Networks'] = num_ntwrks
    
    sni_scored.reset_index(inplace=True)
    
    return sni_scored
    

    
    