import pandas as pd
import streamlit as st


def load_data(data_path):
    raw_data = pd.read_excel(data_path)
    ## Data cleaning
    temp_data = raw_data[raw_data['state'] == 'ended']
    temp_data = temp_data.merge(temp_data[['rental_id', 'delay_at_checkout_in_minutes', 'checkin_type']], 
                            how='left', left_on='previous_ended_rental_id', right_on='rental_id',
                            suffixes=['','_previous'])
    temp_data = temp_data.drop('rental_id_previous', axis=1)
    temp_data['type_issame'] = temp_data['checkin_type'] == temp_data['checkin_type_previous']
    data = temp_data[temp_data['delay_at_checkout_in_minutes_previous'].notna()]

    delay_max = 2000
    data = data[data['delay_at_checkout_in_minutes_previous'] >= -delay_max]
    data = data[data['delay_at_checkout_in_minutes_previous'] <= delay_max]
    data['overlap'] = data['delay_at_checkout_in_minutes_previous'] - data['time_delta_with_previous_rental_in_minutes'] #if overlap negative, then there is enough delta
    data['previous_late'] = data['delay_at_checkout_in_minutes_previous']>0
    data['impacted'] = data['overlap'] > 0

    return data

def preproc_data(data):
    data_late = data.groupby('time_delta_with_previous_rental_in_minutes').agg({'previous_late': ['count', 'sum', 'mean'], 'impacted' : ['sum', 'mean']})                                                                         
    # df.groupby('A').agg({'B': ['min', 'max'], 'C': 'sum'})
    data_late['previous_late', 'countcumsum'] = data_late['previous_late', 'count'].cumsum()
    data_late['previous_late', 'cumsum'] = data_late['previous_late', 'sum'].cumsum()
    data_late['impacted', 'cumsum'] = data_late['impacted', 'sum'].cumsum()
    data_late['impacted_by_lateness'] = data_late['impacted', 'mean']/ data_late['previous_late', 'mean']
    return data_late

def graph_data(data, threshold=720, scope='all'):
    clean_scope = scope.lower()
    if clean_scope != 'all':
        data = data[data['checkin_type'] == clean_scope]
    impacted_loc = data[data['time_delta_with_previous_rental_in_minutes'] < threshold]
    kept_loc = data[data['time_delta_with_previous_rental_in_minutes'] >= threshold]

    impact_graph = preproc_data(impacted_loc)
    kept_graph = preproc_data(kept_loc)

    return impact_graph, kept_graph

def badge_value(data, threshold):
    if threshold == 0:
        return 0
    else:
        return data['previous_late', 'countcumsum'][threshold-30]