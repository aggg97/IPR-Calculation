import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

st.title("IPR Calculation")
st.header("Forcheimer Reservoir Model: ")

forcheimer = ('''The Forcheimer equation expresses the inflow performance in terms of turbulent and non-turbulent pressure drop coefficients expressed as:

*   "a"         the turbulent pressure drop (Non-Darcy Coefficient )
*   "b"         the laminar pressure drop (Non-Darcy Coefficient)

To represent the IPR in a Pressure vs Rate plot then,

$\Delta P^2 = Pws ^2- Pwf^2 = a \cdot Q^2 + b \cdot Q $

$a \cdot Q^2 + b \cdot Q  - (Pws ^2- Pwf^2 ) = 0$

$a \cdot Q^2 + b \cdot Q  - Pws ^2 + Pwf^2 =0 $

$Pwf=\sqrt{Pws ^2-a \cdot Q^2 -b \cdot Q }$
''')

st.markdown(forcheimer)

# Function to fit the curve
def curve_IPR(Q, a, b, Pws, Pwf):
    return np.sqrt(-a * Q ** 2 - b * Q + Pws**2 - Pwf**2)

# Collecting user input
with st.form("Test Data"):
    st.header("Enter Test Data")
    Pws = st.number_input("Enter reservoir pressure (in bar): ")
    
    test_data = []

    while True:
        date = st.date_input("Enter date: ")
        comment = st.text_input("Enter comment: ")
        Pwf = st.number_input("Enter flowing bottomhole pressure (in bar): ")
        Q = st.number_input("Enter rate (in km3/d): ")

        submitted = st.form_submit_button("Add Test") # Button to add a test
        if submitted:
            st.write("Date: ", date, "Comment: ", comment, "BHFP (bar)", Pwf, "Rate (km3/d): ", Q)
            test_data.append((date, comment, Pwf, Q))

        add_more = st.button("Add More Data") # Button to add more test data
        if not add_more:
            break

# Calculate IPR
if st.button("Calculate IPR for test data"):
    Q_data = np.array([d[3] for d in test_data])  # Extracting rate data
    P_data = np.array([d[2] for d in test_data])  # Extracting Pwf data

    initial_guess = [3.75e-9, 4.17e-4]  # Initial guess for the parameters a, b, and c
    bounds = ([0, 0], [np.inf, np.inf])  # Bounds for the parameters

    # Perform curve fitting
    params, _ = curve_fit(curve_IPR, Q_data, P_data, p0=initial_guess, bounds=bounds)
    a_fit, b_fit = params

    st.write("Fitted Parameters:")
    st.write(f"a: {a_fit} bar2/(Sm3/day)2")
    st.write(f"b: {b_fit} bar2/(Sm3/day)")

    # AOF Calculation
    discriminant = b_fit ** 2 + 4 * a_fit * Pws ** 2
    if discriminant >= 0:
        AOF = (-b_fit + np.sqrt(discriminant)) / (2 * a_fit)
        st.write(f"AOF: {AOF/1000} km3/d")
    else:
        st.write("No real roots exist.")

    # Plotting
    Q_range = np.linspace(0, AOF, 500)
    Pwf_fit = curve_IPR(Q_range, a_fit, b_fit, Pws, 0)  # Assuming Pwf as 0 for the plot

    plt.figure()
    plt.scatter(Q_data, P_data, color='red', label='Test Data')
    plt.plot(Q_range, Pwf_fit, color='blue', label='Fitted Curve')
    plt.xlabel('Rate (km3/d)')
    plt.ylabel('Pressure (bar)')
    plt.title('Pressure vs Rate')
    plt.legend()
    st.pyplot(plt)
