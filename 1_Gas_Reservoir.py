import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from tabulate import tabulate

st.title("IPR Calculation")
st.header("Forcheimer Reservoir Model: ")
forcheimer= ('''The Forcheimer equation expresses the inflow performance in terms of turbulent and non turbulent pressure drop coefficients expressed as:

*   "a"         the turbulent pressure drop (Non-Darcy Coefficient )
*   "b"         the laminar pressure drop (Non-Darcy Coefficient)


To represent the IPR in a Pressure vs Rate plot then,

$\Delta P^2 = Pws ^2- Pwf^2 = a \cdot Q^2 + b \cdot Q $


$a \cdot Q^2 + b \cdot Q  - (Pws ^2- Pwf^2 ) = 0$


$a \cdot Q^2 + b \cdot Q  - Pws ^2 + Pwf^2 =0 $


$Pwf=\sqrt{Pws ^2-a \cdot Q^2 -b \cdot Q }$
''')

st.markdown(forcheimer)

Pwf = st.number_input("Enter reservoir pressure (in bar): ")

st.header("Enter test data: ")
date = st.date_input("Enter date: ")
comment = st.text_input("Enter comment: ")
Pwf = st.number_input("Enter flowing bottomhole pressure (in bar): ")
Q = st.number_input("Enter rate (in km3/d): ")

st.button("Calculate IPR for test data")

st.markdown("ahora hay que ver como incorporar muchos tests... se podria poner un boton add test data y que te de las ventanas para cargar datos... algo asi...y como hacer para darle play al codigo que hace la IPR y vincular todo con lo anterior")

with st.form("my_form"):
   st.write("Inside the form")
   slider_val = st.slider("Form slider")
   checkbox_val = st.checkbox("Form checkbox")

   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")
   if submitted:
       st.write("slider", slider_val, "checkbox", checkbox_val)

st.write("Outside the form")
