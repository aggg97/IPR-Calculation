import streamlit as st

st.title("IPR Calculation")

intro=('''This streamlit app contains a pyhton script that will allow you to perform an IPR Calculation for both an oil
and gas reservoir. It collects user input test data to perform a curve fitting using scipy.optimize.curve_fit, 
fitting the Inflow Performance Relationship curve to the data.''')

st.markdown(intro)

col1, col2= st.columns(2)

with col1:
st.page_link("pages/1_Gas_Reservoir.py",color=red, label="Gas Reservoir")

with col2:
st.page_link("pages/2_Oil_Reservoir.py",color=green,  label="Oil Reservoir")
