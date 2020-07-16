def score_CSAQ_frequency(data):    
    r"""
    
    Scores the frequency data from Wilson et al (2003) Cognitively Stimulating 
    Activities Questionnaire as used in the CR/RANN study. Provides frequency 
    of engagement in cognitively stimulating activities at the ages of 6 years,
    12 years, 18 years, 40 years and present age. Also provides total frequency
    of engagement in which frequency at each timepoint is summed.
    
    Parameters
    ----------
    data : dataframe
        Dataframe containing responses for CSAQ questions 1 through 26. Index should contain
        subid.

    Returns
    -------
    csaq_freq : dataframe
        Summary dataframe containing frequency of engagement at each time point and total 
        frequency in following cols: part_A_6; part_B_12; part_C_18; part_D_40; part_E_present;
        part_F_total;
        
    Notes
    -----
    Author: Rory Boyle
    Email: rorytboyle@gmail.com
    Requires: pandas
    Date created: 15/07/2020
    """

    # init df
    csaq_freq = pd.DataFrame()
    
    # score total freq at age 6
    csaq_freq['part_A_6'] = data[['BL_CSAQ_001', 'BL_CSAQ_002', 'BL_CSAQ_003']].sum(
            axis=1, skipna=False) 
    
    # score total freq at age 12
    csaq_freq['part_B_12'] = data.loc[:, 'BL_CSAQ_004':'BL_CSAQ_009'].sum(
            axis=1, skipna=False)
    
    # score total freq at age 18    
    csaq_freq['part_C_18'] = data.loc[:, 'BL_CSAQ_010':'BL_CSAQ_015'].sum(
            axis=1, skipna=False)
    
    # score total freq at age 40  
    csaq_freq['part_D_40'] = data.loc[:, 'BL_CSAQ_017':'BL_CSAQ_021'].sum(
            axis=1, skipna=False)
    
    # score present
    csaq_freq['part_E_present'] = data.loc[:,'BL_CSAQ_022':'BL_CSAQ_026'].sum(
            axis=1, skipna=False)
    
    # score total across all timepoints
    csaq_freq['total'] = csaq_freq.loc[:, 'part_A_6':'part_E_present'].sum(axis=1, skipna=False)
    
    return csaq_freq