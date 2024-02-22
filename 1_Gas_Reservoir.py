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


date = st.date_input("Enter date: ")
comment = st.text_input("Enter comment: ")
Pwf = st.number_input(float(input("Enter flowing bottomhole pressure (in bar): ")))
Q = st.number_input(float(input("Enter rate (in km3/d): ")))

