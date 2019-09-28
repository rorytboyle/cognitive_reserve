data = all_cogRes[['MRN', 'bh101', 'bh102h', 'bh102m', 'bh103', 'bh104h',
                 'bh104m', 'bh105', 'bh106h', 'bh106m', 'bh107']]
data.replace(-1, np.nan, inplace=True) # remove this 
import pandas as pd
import numpy as np


def score_IPAQ_short(IPAQ_data, truncate=True, save_csv=False):
    """
    Scores the IPAQ Short Form following the IPAQ scoring protocol as available
    here: https://sites.google.com/site/theipaq/scoring-protocol or here:
    www.ipaq.ki.se
    Returns a dataframe with scored IPAQ data specifically metabolic minutes
    per week for each activity category and the total metabolic minutes per
    week.
    Note: this function does not clean the data. Please ensure the data is
    cleaned before scoring with this funciton. See above protocol for data
    cleaning instructions. Any missing values should be = 0.

    :param IPAQ_data: pandas dataframe or csv file containing subject ids and
                responses for each subject in the following order:
                    - Column 1 = subject ids
                    - Column 2 =  Q1 (vigorous days)
                    - Column 3 = Q2a (vigorous hours)
                    - Column 4 = Q2b (vigorous mins)
                    - Column 5 = Q3 (moderate days)
                    - Column 6 = Q4a (moderate hours)
                    - Column 7 = Q4b (moderate mins)
                    - Column 8 = Q5 (walking days)
                    - Column 9 = Q6a (walking hours)
                    - Column 10 = Q6b (walking mins)
                    - Column 11 = Q7 (sitting)

                If your csv does not contain subject ids - insert a new column
                with 1 to n (n = total number of subjects) to create a
                'placeholder' subject id.
                All missing data or NaN values should be set to equal 0.
    :param truncate: Flag to choose whether any time values (for a single
                     category e.g. for walking activity) above 180 mins should
                     be truncated to 180 mins. The protocol recommends that any
                     values > 180 mins for an single category should be set to
                     180 mins.
    :param save_csv: Flag to specify whether to save dataframe as a csv in.
                     Will be saved in the current working directory.
    :param X: predictor variable(s)
    :param saveto: folder specifying dir to save results and
                  plots
    :return IPAQ_scored: dataframe with following columns:
                    - Column 1 = subject ids
                    - Column 2 = total mins of vigorous activity per week
                    - Column 3 = total mins of moderate activity per week
                    - Column 4 = total mins of walking per week
                    - Column 5 = total mins of physical activity per week
                    - Column 6 = outlier (i.e. activity > 960 min p/wk)
                    - Column 7 = metabolic mins per week (vigorous)
                    - Column 8 = metabolic mins per week (moderate)
                    - Column 9 = metabolic mins per week (walking)
                    - Column 10 = metabolic mins per week (total)
                    - Column 11 = categorical scores (High/Moderate/Low)
    """
    # read in csv if IPAQ_data is a csv file
    if isinstance(IPAQ_data, pd.DataFrame):
        data = IPAQ_data
    else:
        data = pd.read_csv(IPAQ_data)

    # replace any nan values with 0
    data.replace(np.nan, 0, inplace=True)

    # set up dataframe to be returned
    scored_data = pd.DataFrame()
    scored_data['subid'] = data.iloc[:, 0]  # add subids to new df

    # convert hours + mins into mins only
    data['vigorousMins'] = (data.iloc[:, 2] * 60) + data.iloc[:, 3]
    data['moderateMins'] = (data.iloc[:, 5] * 60) + data.iloc[:, 6]
    data['walkingMins'] = (data.iloc[:, 8] * 60) + data.iloc[:, 9]

    # truncate unless user specifies not to
    # if value in any one column > 180, replace with 180, else retain original
    if truncate:
        data[['vigorousMins', 'moderateMins',
              'walkingMins']] = np.where(data[['vigorousMins', 'moderateMins',
                                               'walkingMins']] > 180, 180,
                                         data[['vigorousMins',
                                               'moderateMins', 'walkingMins']])

    # calculate total time spent in each category = mins * days
    scored_data['vigorousTime'] = data['vigorousMins'] * data.iloc[:, 1]
    scored_data['moderateTime'] = data['moderateMins'] * data.iloc[:, 4]
    scored_data['walkingTime'] = data['walkingMins'] * data.iloc[:, 7]
    scored_data['totalTime'] = scored_data[
            ['vigorousTime', 'moderateTime', 'walkingTime']].sum(
            axis=1)

    # mark any cases with total time > 960 mins as an outlier
    scored_data['outlier'] = np.where(scored_data['totalTime'] > 960,
                                      'Yes', 'No')

    # calculate metabolic minutes for each category
    # vigorous met p/w = 8 * vigorous time
    scored_data['vigorousMET'] = 8 * scored_data['vigorousTime']

    # moderate met p/w = 4.4 * moderate time
    scored_data['moderateMET'] = 4.4 * scored_data['moderateTime']

    # walking met p/w = 3.3 * walking time
    scored_data['walkingMET'] = 3.3 * scored_data['walkingTime']

    # total met p/w
    scored_data['totalMET'] = scored_data[['vigorousMET', 'moderateMET',
                                           'walkingMET']].sum(axis=1)

    # get categorical variables
    # high category
    # high a) 3+ days of vigorous activity  w/ total met mins <= 1500    
    # high b) 7 days of any activity w/ total met mins <= 3000
    
    # moderate category
    # moderate a) 3+ days of <= 20 mins of vigorous activity per day
    # moderate b) 5+ days of <= 30 mins of moderate and/or walking activity
    # moderate c) 5+ days of any activity w/ total met mins <= 600
    # save csv if specified by user
    if save_csv:
        scored_data.to_csv('IPAQ_scored.csv')

    return scored_data
