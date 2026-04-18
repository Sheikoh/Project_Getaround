import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np
import data_calc as dc
import requests

threshold_max = 720
### Data loading
data_path = r"get_around_delay_analysis.xlsx"

data_load_state = st.text('Loading data...')
@st.cache_data # this lets the 
def wrapper_load(data_path):
    return dc.load_data(data_path)

data = wrapper_load(data_path)

# data = pd.read_csv(r"data\data_clean.csv")
data_load_state.text("") # change text from "Loading data..." to "" once the the load_data function has run

## initialization of the session state
if 'threshold' not in st.session_state:
    st.session_state['threshold'] = 0
if 'scope' not in st.session_state:
    st.session_state['scope'] = 'All'

### Data preprocessing
@st.cache_data
def wrapper_preproc(data, threshold, scope):
    return dc.graph_data(data, threshold, scope)

data_impacted, data_kept = wrapper_preproc(data, st.session_state.threshold, st.session_state.scope)


### Title, text and layout

st.title("Project_Get_Around_Dashboard")

# NAVIGATION
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Menu",
    ["Analyse des délais", "Prédiction du prix"],
    index=0
)

## Page 1 - EDA
if page == "Analyse des délais":
    st.subheader("Analyse des délais")
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



# PAGE 2 — API PREDICTION
elif page == "Prédiction du prix":
    st.subheader("Prédiction du prix de location")

    FEATURE_ORDER = [
        "model_key",
        "mileage",
        "engine_power",
        "fuel",
        "paint_color",
        "car_type",
        "private_parking_available",
        "has_gps",
        "has_air_conditioning",
        "automatic_car",
        "has_getaround_connect",
        "has_speed_regulator",
        "winter_tires",
    ]

    API_URL = "https://sheyko-getaround-api.hf.space/predict"

    st.caption(f"API utilisée : {API_URL}")

    with st.form("prediction_form"):
        model_key = st.selectbox("Modèle de voiture", ["Peugeot", "Audi", "BMW"])
        mileage = st.number_input("Kilométrage", value=50000, step=1000)
        engine_power = st.number_input("Puissance moteur", value=100, step=5)
        fuel = st.selectbox("Type de carburant", ["diesel", "petrol", "electric", "hybrid"])
        paint_color = st.selectbox("Couleur", ["black", "white", "grey", "blue", "red"])
        car_type = st.selectbox("Type de voiture", ["sedan", "convertible", "suv", "coupe"])

        private_parking_available = st.checkbox("Parking privé disponible", value=True)
        has_gps = st.checkbox("GPS", value=True)
        has_air_conditioning = st.checkbox("Climatisation", value=True)
        automatic_car = st.checkbox("Boîte automatique", value=True)
        has_getaround_connect = st.checkbox("Getaround Connect", value=True)
        has_speed_regulator = st.checkbox("Régulateur de vitesse", value=True)
        winter_tires = st.checkbox("Pneus hiver", value=True)

        submitted = st.form_submit_button("Prédire le prix")

    if submitted:
        row_dict = {
            "columns": [
                "model_key",
                "mileage",
                "engine_power",
                "fuel",
                "paint_color",
                "car_type",
                "private_parking_available",
                "has_gps",
                "has_air_conditioning",
                "automatic_car",
                "has_getaround_connect",
                "has_speed_regulator",
                "winter_tires"
            ],
            "data": [[
                model_key,
                int(mileage),
                int(engine_power),
                fuel,
                paint_color,
                car_type,
                bool(private_parking_available),
                bool(has_gps),
                bool(has_air_conditioning),
                bool(automatic_car),
                bool(has_getaround_connect),
                bool(has_speed_regulator),
                bool(winter_tires),
            ]]
            
        }

        # row_list = [row_dict[col] for col in FEATURE_ORDER]
        payload = {"input": row_dict}

        try:
            r = requests.post(API_URL, json=payload, timeout=20)
            if r.status_code == 200:
                pred = r.json()["prediction"][0]
                st.success(f"Prix estimé : **{pred:.2f} € / jour**")
            else:
                st.error(f"Erreur {r.status_code}")
                st.code(r.text)
                with st.expander("Payload envoyé"):
                    st.json(payload)
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur lors de la requête : {e}")
            with st.expander("Payload envoyé"):
                st.json(payload)