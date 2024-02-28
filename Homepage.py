import streamlit as st

st.title("IPR Calculation")

intro = '''This Streamlit app contains a Python script that will allow you to perform an IPR Calculation for both an oil
and gas reservoir. It collects user input test data to perform a curve fitting using scipy.optimize.curve_fit, 
fitting the Inflow Performance Relationship curve to the data.'''
st.markdown(intro)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<h3 style="color:red;">Gas Reservoir</h3>', unsafe_allow_html=True)
    st.markdown("[Link to Gas Reservoir](pages/1_Gas_Reservoir.py)")

with col2:
    st.markdown('<h3 style="color:green;">Oil Reservoir</h3>', unsafe_allow_html=True)
    st.markdown("[Link to Oil Reservoir](pages/2_Oil_Reservoir.py)")
