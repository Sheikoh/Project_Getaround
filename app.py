import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np
import data_calc as dc

threshold_max = 720
### Data loading
data_path = 'get_around_delay_analysis.xlsx'

data_load_state = st.text('Loading data...')
@st.cache_data # this lets the 
def wrapper_load(data_path):
    return dc.load_data(data_path)

data = wrapper_load(data_path)

# data = pd.read_csv('data_clean.csv')
data_load_state.text("") # change text from "Loading data..." to "" once the the load_data function has run

## initialization of the session state
if 'threshold' not in st.session_state:
    st.session_state['threshold'] = threshold_max
if 'scope' not in st.session_state:
    st.session_state['scope'] = 'All'

### Data preprocessing
@st.cache_data
def wrapper_preproc(data, threshold, scope):
    return dc.graph_data(data, threshold, scope)

data_impacted, data_kept = wrapper_preproc(data, st.session_state.threshold, st.session_state.scope)


### Title, text and layout

st.title("Project_Get_Around_Dashboard")

## initial graph
st.markdown(""" Below are the preliminary data analyses showing the impact of the delay on the location quality
""")

bar_width = 25
fig = go.Figure()
fig.add_trace(go.Bar(x=data_impacted.index.values, y=data_impacted['previous_late', 'mean']*100, 
                     marker_color = 'lightsalmon', width = bar_width, name = 'prevented_late')) #x=data['time_delta_with_previous_rental_in_minutes'],
fig.add_trace(go.Bar(x=data_impacted.index.values, y=data_impacted['impacted', 'mean']*100 , 
                     marker_color = 'indianred', width = bar_width, name = 'prevented_impacted'))

fig.add_trace(go.Bar(x=data_kept.index.values, y=data_kept['previous_late', 'mean']*100, 
                     marker_color = 'lightblue', width = bar_width, name = 'kept_late')) #x=data['time_delta_with_previous_rental_in_minutes'],
fig.add_trace(go.Bar(x=data_kept.index.values, y=data_kept['impacted', 'mean']*100, 
                     marker_color = 'darkblue', width = bar_width, name = 'kept_impacted'))
fig.update_layout(barmode = 'overlay')

st.plotly_chart(fig, use_container_width=True)
threshold = st.select_slider('threshold', 
                             options=list(range(0,threshold_max+1,30)), 
                             key='threshold', 
                             on_change=wrapper_preproc,
                             kwargs={'data' : data, 
                                    'threshold' : st.session_state.threshold,
                                    'scope' : st.session_state.scope})

## Threshold application
st.markdown("""Effect of the application of the threshold and its scope of application """)
col1, col2, col3 = st.columns(3)

with col1:
    st.header("Parameter choice")
    st.badge(f"Threshold: {threshold}", color="green")
    scope = st.selectbox("Scope:", 
                         ["All", "Connect", "Mobile"],
                         key='scope',
                         on_change=wrapper_preproc,
                         kwargs={'data' : data, 
                                 'threshold' : st.session_state.threshold,
                                 'scope' : st.session_state.scope}
                         )


with col2:
    st.header("Rentals affected")
    st.badge(f'{dc.badge_value(data_impacted, threshold)}', color='red', width='stretch')



with col3:
    st.header("Problems solved")
    st.badge(f'{dc.badge_value(data_impacted, threshold)}', width='stretch')



