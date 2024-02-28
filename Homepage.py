import streamlit as st

st.title("IPR Calculation")

intro = '''This Streamlit app contains a Python script that will allow you to perform an IPR Calculation for both an oil
and gas reservoir. It collects user input test data to perform a curve fitting using scipy.optimize.curve_fit, 
fitting the Inflow Performance Relationship curve to the data.'''
st.markdown(intro)

col1, col2 = st.columns(2)



    st.page_link("pages/1_Gas_Reservoir.py", label="Gas Reservoir", class_name="red-text")


    st.page_link("pages/2_Oil_Reservoir.py", label="Oil Reservoir", class_name="green-text")
