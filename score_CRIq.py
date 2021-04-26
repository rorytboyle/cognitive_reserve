def score_CRIq(df):
    """
    Scores the Cognitive Reserve Index Questionnaire following the 
    instructions outlined in http://www.cognitivereserveindex.org/Nucci_et_al_12a.pdf

    Note: this function does not clean the data. Please ensure the data is
    cleaned before scoring with this function.Any missing values should be = 0.
    
    @author: Rory Boyle rorytboyle@gmail.com
    @date: 21/04/2021

    :param df: pandas dataframe (or .csv file) of size p * 43 (p = number of 
                participants). Cols = subid, age, and then CRIq responses.
                CRIq response should be in order as in the pen and paper 
                questionnaire i.e. Education (2 questions + 
                2 responses), Working Activity (5 questions + 5 responses),
                Leisure Time Weekly Frequency (5 questions + 10 responses),
                Leisure Time Monthly Frequency (6 questions + 12 responses),
                Leisure Time Annual Frequency (3 questions + 6 responses), &
                Leisure Time Fixed Frequency (3 questions + 6 responses).
                Leisure Time questions have two responses (weekly frequency
                & number of years in which activity has been carried out).
                Leisure Time responses must be exactly in order as pen and 
                paper questionnaire (e.g. LeisureTime q 1.1 = Frequency of
                reading newspapers and magazines, Leisure Time q 1.1a = Years
                of reading newspapers and magazines, Leisure Time q 1.2 = 
                Frequency of domestic chores, Leisure Time q 1.2a = Years of 
                domestic chores.)
                Leisure Time responses must be coded as 0 (Never/Rarely) and
                1 (Often/Always).
                All missing data or NaN values should be set to equal 0.

    :return CRIq_standardised: dataframe with CRIq scores with following 
                columns:
                    - Column 1 (subid) = participant id
                    - Column 2 (CRIq_edu) = education subscore (standardised)
                    - Column 3 (CRIq_working) = working activity subscore (standardised)
                    - Column 4 (CRIq_leisure) = leisure time subscore (standardised)
                    - Column 5 (CRIq_total) = total score (standardised)
    """
    import pandas    
    import math
    import numpy
    #%% 1) Prep dataframe
    CRIq_raw = pd.DataFrame(columns=['subid', 'edu_raw', 'working_raw',
                                     'leisure_raw'])
    CRIq_standardised = pd.DataFrame(columns=['subid', 'edu', 'working',
                                     'leisure', 'total'])
    
    CRIq_raw['subid'] = df.iloc[:,0]
    CRIq_standardised['subid'] = df.iloc[:,0]
          
    # Check for any participants with 0s in raw questionnaire answers
    df.set_index('subid', inplace=True)
    zero_rows = (df==0).all(axis=1)  # retain for end to replace final scores
    df.reset_index(inplace=True)     # with NaNs for ppts without answers
    
    #%% 2) Get edu subscores
    # "raw score of this section is the sum of these two values"
    CRIq_raw['edu_raw'] = df.iloc[:, 2:4].sum(axis=1)
    
    # preset coefficients (from CRIq scoring spreadsheet)
    edu_intercept = 21.1691293
    edu_slope = -0.1642092
    edu_std = 4.749805
    
    # get expected values for age
    expected_edu = (df['age']*edu_slope) + edu_intercept
    
    # calculate edu residual
    edu_residual = (CRIq_raw['edu_raw'] - expected_edu) / edu_std

    # scale
    CRIq_standardised['edu'] = (edu_residual * 15)+100
        
    #%% 2) Calculate working activity subscore      
    # round values up to nearest 5 (as instructed in paper scale)
    def roundup(x):
        return int(math.ceil(x / 5)) * 5   
    df.iloc[:, 4:9] = df.iloc[:, 4:9].applymap(roundup)
    
    # multiply years by job level
    for level in range(1,6):
        ix = level+3
        df.iloc[:, ix] = df.iloc[:, ix] * level
        
    # set zeros to nan
    df.iloc[:, 4:9] = df.iloc[:, 4:9].replace(0, np.nan)
    
    # get max working activity score for each ppt and save in separate series
    max_working = df.iloc[:, 4:9].max(axis=1)
    
    # get index of max
    max_ix = df.iloc[:, 4:9].idxmax(axis=1)

    # loop through df and get average of other scores (without max score)
    avg_working = pd.Series(index=max_working.index)
    
    for row in range(len(max_ix)):
        # get all working activity responses for ppt in row
        all_work = df.iloc[row, 4:9]

        # replace max value with nan
        all_work[max_ix.iloc[row]] = np.nan
        
        # IF MORE THAN THREE WORKING ACTIVITY ENTRIES, DROP LOWEST ENTRY
        # THIS PUTS CODE IN LINE WITH EXCEL SCORING SHEET WHICH ONLY ALLOWS
        # 3 ENTRIES. >= 3 used in this code here because max entry already set to NaN
        if all_work.count() >= 3:
            all_work[all_work.idxmin()] = np.nan

        # get mean working activity score without the max value
        avg_working[row] = all_work.mean()
     
    # replace avg_working nans with zeros to enable sum in next step
    avg_working.replace(np.nan, 0, inplace=True)
    
    # add highest value for working activity score to average of other working
    # activity values
    CRIq_raw['working_raw'] = max_working + avg_working
           
    # preset coefficients (from CRIq scoring spreadsheet)
    working_intercept = -2.082
    working_slope = 1.124
    working_std = 40.21979
    
    # get expected values for age
    expected_working = (df['age']*working_slope + working_intercept)
    
    # calculate working activity residual
    working_residual = (CRIq_raw['working_raw'] - expected_working) / working_std

    # scale
    CRIq_standardised['working'] = (working_residual * 15)+100
     
    #%% 3) Calculate leisure time subscore
    # get leisure activity columns (i.e. all leisure responses
    # except for question on children) and children responses separately
    activity_cols = list(range(9,37)) + list(range(39,43))
    leisure_activity = df.iloc[:, activity_cols]
    children = df.iloc[:, 37:39]

    # get frequency columns and year columns separately
    leisure_freq = leisure_activity[leisure_activity.columns[::2]]
    leisure_years = leisure_activity[leisure_activity.columns[1::2]]

    # round up all leisure activity years columns by 5
    leisure_years = leisure_years.applymap(roundup)
    
    # get raw leisure activity score (multiply frequency by years for each q)
    leisure_activity_raw = pd.DataFrame(leisure_years.values * 
                                        leisure_freq.values, 
                                        columns=leisure_freq.columns).sum(axis=1)
       
    # get children columns
    # get score for children (multiply number of children by 5 and then add 10)
    children_raw = (children.iloc[:,1] * 5) + 10
    
    # no children = score of 0 
    children_raw.replace(10, 0, inplace=True)
    
    CRIq_raw['leisure_raw'] = leisure_activity_raw + children_raw
    
    # preset coefficients (from CRIq scoring spreadsheet)
    leisure_intercept = 2.68
    leisure_slope = 3.754
    leisure_std = 80.24101
    
    # get expected values for age
    expected_leisure = (df['age']*leisure_slope) + leisure_intercept
    
    # calculate leisure residual
    leisure_residual = (CRIq_raw['leisure_raw'] - expected_leisure) / leisure_std

    # scale
    CRIq_standardised['leisure'] = (leisure_residual * 15)+100
    
    #%% 4) Calculate total CRIq score
    # replace nans with zeros to account for scores of zero (e.g. in working 
    # activity)
    CRIq_standardised.replace(np.nan, 0, inplace=True)
    
    # get avg of three subscores
    CRIq_standardised['total'] = CRIq_standardised.iloc[:, 1:4].mean(axis=1)
    
    # scale total score
    CRIq_standardised['total'] = ((((CRIq_standardised['total']-100)/11.32277)*15)+100)
    
    #%% 5) Set values for any participants who didn't answer questionnaire (e.g.
    # answers were all zero) to NaN - if this is skipped, they will still be 
    # given a score despite not answering questionnaire
    
    # Replace scores for these participants with NaNs in final CRIq scores
    CRIq_standardised.set_index('subid', inplace=True)
    CRIq_standardised[zero_rows] = np.nan
    CRIq_standardised.reset_index(inplace=True)
    
    return CRIq_standardised
