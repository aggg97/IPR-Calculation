import streamlit as st

st.title("Inflow Performance Curve (IPR) Calculation")

intro = '''This Streamlit app contains a Python script that will allow you to perform an IPR Calculation for both an oil
and gas reservoir. It collects user input test data to perform a curve fitting using scipy.optimize.curve_fit, 
fitting the Inflow Performance Relationship curve to the data.'''

st.markdown(intro)

col1, col2,col3 = st.columns(3)

with col1:
    st.markdown('<h3 style="color:red;">Gas Reservoir</h3>', unsafe_allow_html=True)
    st.markdown("IPR Calculation using Forcheimer model")
    st.page_link("pages/1_Gas_Reservoir.py", label="<b>click here</b>")

with col2:
    st.markdown('<h3 style="color:green;">Oil Reservoir</h3>', unsafe_allow_html=True)
    st.markdown("IPR Calculation using Vogel quadratic equation")
    st.page_link("pages/2_Oil_Reservoir.py", label="<b>click here</b>")

with col3:
    st.markdown('<h3 style="color:blue;">Multiwell IPR Calculation</h3>', unsafe_allow_html=True)
    st.markdown("By uploading a .csv file with test data for different wells, IPR calculation will be done with either Forcheimer's or Vogel's IPR cuadratic equation")
    st.page_link("pages/3_Multiwell_IPR_Calculation.py", label="<b>click here</b>")

st.divider()
