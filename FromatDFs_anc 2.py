"""
Add description
"""

from pathlib import Path
import numpy as np
import seaborn as sns
from tqdm import tqdm
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
pd.set_option('mode.chained_assignment', None)

# ==============================================
# Initialize dataframe for all sessions across all experiments
trials_df = pd.DataFrame()

LT_group1 = ['bella', 'kuemmel', 'renate', 'leni']
LT_group2 = ['fenja', 'granny']
CM_AUT_list = ['f', 'k', 'c', 'd']

df_filename = "AllTrialsDF.csv"
CM_metaData = 'Animals_metaData.csv'
directory_name = Path("data/")

data_files = os.listdir(directory_name)
data_files = sorted(list(filter(lambda f: f.endswith('.csv'), data_files)))

# Cycle through the data files
for file in data_files:
    if 'CM' in file:
        if 'AUT' in file:
            print('===> Processing marmoset data: ' + file)
            # ====================================================================
            # 1) Open and process the dataframe
            csv_file = directory_name / file
            df = pd.read_csv(csv_file, low_memory=False, decimal=',')

            # Remove rows with non assigned animals, with one animal that left early, and from testing sessions
            df['monkey'] = df['monkey'].loc[~df['monkey'].isin(['nn', 'nan', 'closina', 'test'])]
            df = df.loc[df.monkey.isin(list(df['monkey'].dropna().unique()))]

            # Reformat a few column names
            df.rename(columns={"animalsExpectedPerMxbi": "animalsExpected"}, inplace=True)
            df.rename(columns={"session": "sessionNumber"}, inplace=True)
            df.rename(columns={"animal": "monkey"}, inplace=True)

            # Fix one animal's name inconsistencies
            df['animalsExpected'] = df['animalsExpected'].replace('innotiza', 'innotizia', regex=True)

            # fix date and timestamp formatting
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['timestamp'] = df['timestamp'].astype(float)

            # Convert date into day and time of each session
            df['day'] = pd.to_datetime(df['date'], format='%Y:%M:%D').dt.date
            df['time'] = pd.to_datetime(df['date'], format='%Y:%M:%D').dt.time

            AnimalDictionary = pd.read_csv(CM_metaData, low_memory=False, sep=';')
            for m in AnimalDictionary.monkey.unique():
                df['monkey'] = df['monkey'].replace({m: AnimalDictionary[AnimalDictionary.monkey == m].ID.to_list()})

                df['animalsExpected'] = \
                    df['animalsExpected'].str.replace(m, AnimalDictionary[AnimalDictionary.monkey == m].ID.values[0])

            # Check if exists and format the column animalsExpected
            df["animalsExpected"] = df["animalsExpected"].apply(eval)

            # Only consider the animals who run the entire staircase
            df = df.loc[df.monkey.isin(CM_AUT_list)]

            # reset the index
            df = df.reset_index(drop=True)

            # ====================================================================
            df['date'] = pd.to_datetime(df.date, format='%Y-%m-%d')
            df['date'] = df['date'].dt.normalize()

            # only take valid steps from the AUT (range 1 to 50)
            df = df.loc[(df['step'] > 1)]
            df = df.loc[(df['step'] < 50)]

            # only take versions of the AUT that contain the same steps of version 10
            df = df.loc[(df['version'] >= 8)]

            # filter the temporary dataframe (AUT_df) with outcome information
            df.loc[df['object'].str.contains('correct'), 'object'] = 'reward'
            df.loc[df['object'].str.contains('wrong'), 'object'] = 'wrong'
            df.loc[df['object'].str.contains('ign'), 'object'] = 'ignore'
            df.loc[df['object'].str.contains('start'), 'object'] = 'start'

            # Duplicate the dataframe
            df2 = df.loc[(df['object'] == 'reward') | (df['object'] == 'wrong') |
                        (df['object'] == 'ignore') | (df['object'] == 'start')]

            # sort the staircase by session number and version
            df2 = df2.sort_values(by=['sessionNumber', 'version'], ignore_index=True)

            # Cycle through the each animal, date, and trial
            for m in CM_AUT_list:
                unique_dates = df2[df2['monkey'] == m]['date'].unique()
                for d in tqdm(range(0, len(unique_dates))):
                    # print('-> Processing monkey ' + m)
                    for t in df2[(df2['monkey'] == m) & (df2['date'] == unique_dates[d])]['trial'].unique():

                        A = df2[(df2['monkey'] == m) & (df2['date'] == unique_dates[d]) & (df2['trial'] == t)].reset_index()
                        B = df2[(df2['monkey'] == m) & (df2['date'] == unique_dates[d]) & (df2['object'] == 'start')].reset_index()
                        C = df2[(df2['date'] == unique_dates[d]) & (df2['object'] == 'start')].reset_index()

                        if (len(A) == 2) & (A['object'][0] == 'start'):
                            trials_df = trials_df.append({
                                'trial': t,
                                'date': A.loc[0,'date'],
                                'time': A.loc[0,'time'],
                                'trial_timestamp': A.loc[0, 'timestamp'],
                                'task': A.loc[0,'type'],
                                'outcome_timestamp': A.loc[1, 'timestamp'],
                                'outcome': A.loc[1, 'object'],
                                'step': A.loc[0, 'step'],
                                'session': A.loc[0, 'sessionNumber'],
                                'device': A.loc[0, 'mxbi'],
                                'fluid': 'during',
                                'food': 'during',
                                'duration': C["timestamp"].iloc[-1] /60000,
                                'experiment': A.loc[0, 'experiment'],
                                'animal': m,
                                'isolation': 'no',
                                'species': 'marmoset',
                                'group': C['animalsExpected'].iloc[-1],
                                'total_trials': len(B)},
                                ignore_index=True)

            trials_df = trials_df.sort_values(by=['species', 'animal', 'date', 'trial_timestamp'])
            trials_df = trials_df.reset_index(drop=True)

        if '2AC' in file:
            print('===> Processing marmoset data: ' + file)
            # ====================================================================
            # 1) Open and process the dataframe
            csv_file = directory_name / file
            df = pd.read_csv(csv_file, low_memory=False, decimal=',')

            # Remove rows with non assigned animals, with one animal that left early, and from testing sessions
            df['monkey'] = df['monkey'].loc[~df['monkey'].isin(['nn', 'nan', 'closina', 'test'])]
            df = df.loc[df.monkey.isin(list(df['monkey'].dropna().unique()))]

            # Reformat a few column names
            df.rename(columns={"animalsExpectedPerMxbi": "animalsExpected"}, inplace=True)
            df.rename(columns={"session": "sessionNumber"}, inplace=True)
            df.rename(columns={"animal": "monkey"}, inplace=True)

            # Fix one animal's name inconsistencies
            df['animalsExpected'] = df['animalsExpected'].replace('innotiza', 'innotizia', regex=True)

            # fix date and timestamp formatting
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['timestamp'] = df['timestamp'].astype(float)

            # Convert date into day and time of each session
            df['day'] = pd.to_datetime(df['date'], format='%Y:%M:%D').dt.date
            df['time'] = pd.to_datetime(df['date'], format='%Y:%M:%D').dt.time

            AnimalDictionary = pd.read_csv(CM_metaData, low_memory=False, sep=';')
            for m in AnimalDictionary.monkey.unique():
                df['monkey'] = df['monkey'].replace({m: AnimalDictionary[AnimalDictionary.monkey == m].ID.to_list()})

                df['animalsExpected'] = \
                    df['animalsExpected'].str.replace(m, AnimalDictionary[AnimalDictionary.monkey == m].ID.values[0])

            # Check if exists and format the column animalsExpected
            df["animalsExpected"] = df["animalsExpected"].apply(eval)

            # reset the index
            df = df.reset_index(drop=True)

            # ====================================================================
            df['date'] = pd.to_datetime(df.date, format='%Y-%m-%d')
            df['date'] = df['date'].dt.normalize()

            # filter the temporary dataframe (AUT_df) with outcome information
            df.loc[df['object'].str.contains('correct'), 'object'] = 'reward'
            df.loc[df['object'].str.contains('wrong'), 'object'] = 'wrong'
            df.loc[df['object'].str.contains('ign'), 'object'] = 'ignore'
            df.loc[df['object'].str.contains('start'), 'object'] = 'start'

            # Duplicate the dataframe
            df2 = df.loc[(df['object'] == 'reward') | (df['object'] == 'wrong') |
                         (df['object'] == 'ignore') | (df['object'] == 'start')]

            # sort the staircase by session number and version
            df2 = df2.sort_values(by=['sessionNumber', 'version'], ignore_index=True)

            # Cycle through each animal, date, and trial
            for m in df2.monkey.unique():
                unique_dates = df2[df2['monkey'] == m]['date'].unique()
                for d in tqdm(range(0, len(unique_dates))):
                    for t in df2[(df2['monkey'] == m) & (df2['date'] == unique_dates[d])]['trial'].unique():

                        A = df2[(df2['monkey'] == m) & (df2['date'] == unique_dates[d]) & (df2['trial'] == t)].reset_index()
                        B = df2[(df2['monkey'] == m) & (df2['date'] == unique_dates[d]) & (df2['object'] == 'start')].reset_index()
                        C = df2[(df2['date'] == unique_dates[d]) & (df2['object'] == 'start')].reset_index()

                        if (len(A) == 2) & (A['object'][0] == 'start'):
                            trials_df = trials_df.append({
                                'species': 'marmoset',
                                'animal': m,
                                'date': A.loc[0, 'date'],
                                'trial_timestamp': A.loc[0, 'timestamp'],
                                'trial': t,
                                'time': A.loc[0, 'time'],
                                'task': A.loc[0, 'type'],
                                'outcome_timestamp': A.loc[1, 'timestamp'],
                                'outcome': A.loc[1, 'object'],
                                'session': A.loc[0, 'sessionNumber'],
                                'device': A.loc[0, 'mxbi'],
                                'fluid': 'during',
                                'food': 'during',
                                'isolation': 'no',
                                'duration': C["timestamp"].iloc[-1] / 60000,
                                'experiment': A.loc[0, 'experiment'],
                                'group': C['animalsExpected'].iloc[-1],
                                'total_trials': len(B)},
                                ignore_index=True)

            trials_df = trials_df.sort_values(by=['species', 'animal', 'date', 'trial_timestamp'])
            trials_df = trials_df.reset_index(drop=True)

    if 'LT' in file:
        print('===> Processing long-tailed data:' + file)
        # ====================================================================
        # 1) Open and process the dataframe
        csv_file = directory_name / file
        df = pd.read_csv(csv_file, low_memory=False, decimal=',')

        # create animalsExpected column
        df['animalsExpected'] = np.nan
        df['animalsExpected'].loc[df['monkey'].isin(LT_group1)] = str(LT_group1)
        df['animalsExpected'].loc[df['monkey'].isin(LT_group2)] = str(LT_group2)

        # Reformat a few column names
        df.rename(columns={"session": "sessionNumber"}, inplace=True)
        df.rename(columns={"animal": "monkey"}, inplace=True)

        # Check if exists and format the column animalsExpected
        df["animalsExpected"] = df["animalsExpected"].apply(eval)

        # Reformat date and time columns
        df['time'] = df['date'].astype(str).str[-6:].astype(np.int64)
        df['date'] = df['date'].astype(str).str[0:-6].astype(np.int64)

        df['date'] = pd.to_datetime(df.date, format='%Y%m%d').dt.date
        df['time'] = pd.to_datetime(df.time, format='%H%M%S').dt.time

        # Sort by date
        df = df.sort_values(by=['date', 'monkey', 'timestamp']).reset_index(drop=True)

        # ====================================================================
        # Homogenize trial outcomes and trial start identifiers across AUT steps and task versions
        df.loc[df['object'].str.contains('reward'), 'object'] = 'reward'
        df.loc[df['object'].str.contains('wrong'), 'object'] = 'wrong'
        df.loc[df['object'].str.contains('ign'), 'object'] = 'ignore'
        df.loc[df['object'].str.contains('touched'), 'object'] = 'start'

        # Remove unnecessary AUT steps
        df = df.loc[((df['step'] < 49) & (df['step'] >-1)) & (df['trial'] >0)]

        # Duplicate the dataframe and isolate only trial starts and ends
        df = df.loc[(df['object'] == 'reward') | (df['object'] == 'wrong') |
                     (df['object'] == 'ignore') | (df['object'] == 'start')].reset_index(drop=True)

        # Optimize DF sorting for looping
        df = df.sort_values(by=['monkey', 'date', 'timestamp'], ignore_index=True)
        df2 = df.copy(deep=False)

        # Cycle through each animal, date, and trial
        for m in df.monkey.unique():
            unique_dates = df[df['monkey'] == m]['date'].unique()
            for d in tqdm(range(0, len(unique_dates))):
                for t in df[(df['monkey'] == m) & (df['date'] == unique_dates[d])]['trial'].unique():

                    A = df[(df['monkey'] == m) & (df['date'] == unique_dates[d]) & (df['trial'] == t)].reset_index()
                    B = df[(df['monkey'] == m) & (df['date'] == unique_dates[d]) & (df['object'] == 'start')].reset_index()
                    C = df2[(df2['date'] == unique_dates[d])].reset_index()
                    C = C.sort_values(by=['time'], ignore_index=True)

                    if (len(A) == 2) & (A['object'][0] == 'start'):
                        trials_df = trials_df.append({
                            'species': 'longtail',
                            'animal': m,
                            'date': A.loc[0, 'date'],
                            'trial_timestamp': A.loc[0, 'timestamp'],
                            'trial': t,
                            'time': A.loc[0, 'time'],
                            'task': '2AC',
                            'step': A.loc[0, 'step'],
                            'outcome_timestamp': A.loc[1, 'timestamp'],
                            'outcome': A.loc[1, 'object'],
                            'session': A.loc[0, 'sessionNumber'],
                            'device': 'LXBI',
                            'fluid': 'during',
                            'food': 'during',
                            'isolation': 'no',
                            'duration': C["timestamp"].iloc[-1] / 60000,
                            'experiment': 'AUT',
                            'group': C['animalsExpected'].iloc[-1],
                            'total_trials': len(B)},
                            ignore_index=True)

        trials_df = trials_df.sort_values(by=['species', 'animal', 'date', 'trial_timestamp'])
        trials_df = trials_df.reset_index(drop=True)

    if ('RM' in file) & ('MCI' in file):
        print('===> Processing Rhesus Macaques data: ' + file)
        # ====================================================================
        # 1) Open and process the dataframe
        csv_file = directory_name / file
        df = pd.read_csv(csv_file, low_memory=False, decimal=',')
        df.rename(columns={"manual_label": "monkey"}, inplace=True)

        df['date'] = pd.to_datetime(df.date, format='%Y%m%d')

        for m in df['monkey'].unique():
            unique_dates = df[df['monkey'] == m]['date'].unique()

            for d in tqdm(range(0, len(unique_dates))):
                A = df[(df['date'] == unique_dates[d]) & (df['monkey'] == m)].reset_index()
                B = df[(df['group'] == A['group'].unique()[0]) & (df['date'] == unique_dates[d])].reset_index()

                for t in range(0,len(A)):
                    trials_df = trials_df.append({
                        'trial': A.loc[t, 'trial'],
                        'date': A.loc[t, 'date'],
                        'time': A.loc[t, 'time_of_day'],
                        'trial_timestamp': A.loc[t, 'trial_start'],
                        'task': A.loc[t, 'selection'],
                        'stimulus_size': A.loc[t, 'size'],
                        'stimulus_speed': A.loc[t, 'speed'],
                        'outcome_timestamp': A.loc[t, 'outcomeTime'] / 1000,
                        'outcome': A.loc[t, 'outcome'],
                        'session': A.loc[t, 'date'],
                        'device': A.loc[t, 'xbi'],
                        'fluid': 'during',
                        'food': 'during',
                        'duration': A.loc[t, 'session_end'] / 60000000,
                        'experiment': 'MCI',
                        'animal': m,
                        'isolation': 'no',
                        'species': 'rhesus',
                        'group': A['group'].unique(),
                        'total_trials': len(A)},
                        ignore_index=True)

        # sort the new dataframe and reset its index
        trials_df = trials_df.sort_values(by=['species', 'animal', 'date', 'trial_timestamp'])
        trials_df = trials_df.reset_index(drop=True)

    if ('RM' in file) & ('AUT' in file):
        print('===> Processing Rhesus Macaques data: ' + file)
        # ====================================================================
        # 1) Open and process the dataframe
        csv_file = directory_name / file
        df = pd.read_csv(csv_file, low_memory=False, decimal=',')
        df.rename(columns={"subjID": "monkey"}, inplace=True)
        df = df.loc[df.monkey.isin(list(df['monkey'].dropna().unique()))]

        df['date'] = pd.to_datetime(df.date, format='%Y%m%d')

        df.loc[df['outcome'] == 1, 'outcome'] = 'reward'
        df.loc[df['outcome'] == 0, 'outcome'] = 'wrong'

        for m in df['monkey'].unique():
            unique_dates = df[df['monkey'] == m]['date'].unique()

            for d in tqdm(range(0, len(unique_dates))):
                A = df[(df['date'] == unique_dates[d]) & (df['monkey'] == m)].reset_index()

                for t in range(0,len(A)):
                    trials_df = trials_df.append({
                        'trial': A.loc[t, 'trial'],
                        'date': A.loc[t, 'date'],
                        'trial_timestamp': A.loc[t, 'trialStart'] / 1000,
                        'task': '4AC',
                        'outcome_timestamp': A.loc[t, 'trialEnd'] / 1000,
                        'outcome': A.loc[t, 'outcome'],
                        'step': A.loc[t, 'step'],
                        'session': A.loc[t, 'date'],
                        'fluid': 'before&after',
                        'food': 'after',
                        'duration': A.loc[t, 'sessionEnd'] / 60000000,
                        'experiment': 'AUT',
                        'animal': m,
                        'isolation': 'yes',
                        'species': 'rhesus',
                        'group': m,
                        'total_trials': len(A)},
                        ignore_index=True)

        # sort the new dataframe and reset its index
        trials_df = trials_df.sort_values(by=['species', 'animal', 'date', 'trial_timestamp'])
        trials_df = trials_df.reset_index(drop=True)

    if ('RM' in file) & ('MDSS' in file):
        print('===> Processing Rhesus Macaques data: ' + file)
        # ====================================================================
        # 1) Open and process the dataframe
        csv_file = directory_name / file
        df = pd.read_csv(csv_file, low_memory=False, decimal=',')
        df.rename(columns={"subjID": "monkey"}, inplace=True)
        df = df.loc[df.monkey.isin(list(df['monkey'].dropna().unique()))]

        df['date'] = pd.to_datetime(df.date, format='%Y%m%d')

        df.loc[df['outcome'] == 1, 'outcome'] = 'reward'
        df.loc[df['outcome'] == 0, 'outcome'] = 'wrong'

        for m in df['monkey'].unique():
            unique_dates = df[df['monkey'] == m]['date'].unique()

            for d in tqdm(range(0, len(unique_dates))):
                A = df[(df['date'] == unique_dates[d]) & (df['monkey'] == m)].reset_index()

                for t in range(0,len(A)):
                    trials_df = trials_df.append({
                        'trial': A.loc[t, 'trial'],
                        'date': A.loc[t, 'date'],
                        'trial_timestamp': A.loc[t, 'trialStart'] / 1000,
                        'task': '4AC',
                        'outcome_timestamp': A.loc[t, 'trialEnd'] / 1000,
                        'outcome': A.loc[t, 'outcome'],
                        'session': A.loc[t, 'date'],
                        'fluid': 'before&after',
                        'food': 'after',
                        'isolation': 'yes',
                        'duration': A.loc[t, 'sessionEnd'] / 60000000,
                        'experiment': 'MDSS',
                        'animal': m,
                        'species': 'rhesus',
                        'group': m,
                        'total_trials': len(A)},
                        ignore_index=True)

        # sort the new dataframe and reset its index
        trials_df = trials_df.sort_values(by=['species', 'animal', 'date', 'trial_timestamp'])
        trials_df = trials_df.reset_index(drop=True)

# ========
# Load the dataframe
trials_df = pd.read_csv(df_filename, low_memory=False, decimal=',')

# sort the columns to an arbitrary order
trials_df = trials_df[['species', 'animal', 'trial', 'trial_timestamp', 'date', 'time', 'outcome', 'outcome_timestamp',
                       'step', 'experiment', 'task', 'device', 'group', 'duration', 'total_trials',
                       'fluid', 'food', 'isolation', 'stimulus_size', 'stimulus_speed']]

# sort the rows
trials_df = trials_df.sort_values(by=['species', 'date', 'trial'])

# Set columns to string type
trials_df['species'] = trials_df['species'].astype(str)
trials_df['animal'] = trials_df['animal'].astype(str)
trials_df['outcome'] = trials_df['outcome'].astype(str)
trials_df['experiment'] = trials_df['experiment'].astype(str)
trials_df['task'] = trials_df['task'].astype(str)
trials_df['device'] = trials_df['device'].astype(str)
trials_df['food'] = trials_df['food'].astype(str)
trials_df['fluid'] = trials_df['fluid'].astype(str)
trials_df['isolation'] = trials_df['isolation'].astype(str)

# Set columns to integers
trials_df['trial'] = trials_df['trial'].astype(int)
trials_df['trial_timestamp'] = trials_df['trial_timestamp'].astype(float)
trials_df['trial_timestamp'] = trials_df['trial_timestamp'].astype(int)
trials_df['outcome_timestamp'] = trials_df['outcome_timestamp'].astype(float)
trials_df['outcome_timestamp'] = trials_df['outcome_timestamp'].astype(int)
trials_df['total_trials'] = trials_df['total_trials'].astype(int)
trials_df['step'] = trials_df['step'].astype(float)
trials_df['step'] = trials_df['step'].astype('Int64')

# Homogenize DF
trials_df.loc[trials_df['outcome'].str.contains('hit'), 'outcome'] = 'reward'
trials_df.loc[trials_df['experiment'].str.contains('detection'), 'experiment'] = 'Acoustic Detection'
trials_df.loc[trials_df['experiment'].str.contains('discrimination'), 'experiment'] = 'Acoustic Discrimination'
trials_df = trials_df.loc[trials_df['outcome'] != 'start'].reset_index(drop=True)

trials_df.to_csv(df_filename, sep=',', index=False)


