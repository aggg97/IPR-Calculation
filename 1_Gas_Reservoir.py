import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

st.title("IPR Calculation")

# Definition of the quadratic curve equation (Inflow Performance Relationship - IPR)
def curve_IPR(Q, a, b, Pws):
    return np.sqrt(-a * Q ** 2 - b * Q + Pws ** 2)

# Function to perform curve fitting and calculations
def calculate_IPR(data, Pws):
    # Convert data into arrays
    Q_data = np.array([d[3] for d in data])
    P_data = np.array([d[2] for d in data])

    # Perform curve fitting
    initial_guess = [3.75e-9, 4.17e-4]  # Initial guess for the parameters a, b, and c
    bounds = ([0, 0], [np.inf, np.inf])  # Bounds for the parameters
    params, _ = curve_fit(curve_IPR, Q_data, P_data, p0=initial_guess, bounds=bounds)
    a_fit, b_fit = params

    st.write("\n\nFitted Parameters:")
    st.write(f"a: {a_fit:.2f} bar2/(Sm3/day)2")
    st.write(f"b: {b_fit:.2f} bar2/(Sm3/day)")
    st.write(f"Reservoir Pressure: {Pws:.2f} bar")

    # AOF Calculation
    # Bhaskara’s formula to find positive root
    discriminant = b_fit ** 2 + 4 * a_fit * Pws ** 2
    if discriminant >= 0:
        AOF = (-b_fit + np.sqrt(discriminant)) / (2 * a_fit)
        st.write(f"AOF: {AOF / 1000:.2f} km3/d")
    else:
        st.write("No real roots exist.")

    # Range of points for extrapolation of the curve
    Q_range = np.linspace(0, AOF, 500)
    Pwf_fit = curve_IPR(Q_range, a_fit, b_fit, Pws)

    # Test points
    plt.scatter(Q_data, P_data, color='red', label='Test Data')
    # Fitted curve
    plt.plot(Q_range, Pwf_fit, color='blue', label='Fitted Curve')

    # Set the limits for both x and y axes
    plt.xlim(0, plt.xlim()[1])  # x-axis minimum to 0
    plt.ylim(0, plt.ylim()[1])  # y-axis minimum to 0

    plt.xlabel('Rate (km$^3$/ d)')
    plt.ylabel('Pressure (bar)')
    plt.title('Pressure vs Rate')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

# Collect first test data
st.write("Enter reservoir pressure:")
Pws = st.number_input("Pressure (bar)")

data = []
st.write("Enter test data:")
date = st.text_input("Date:")
comment = st.text_input("Comment:")
Pwf = st.number_input("Flowing bottomhole pressure (bar):")
Q = st.number_input("Rate (km3/d):")
data.append((date, comment, Pwf, Q))

# Option to add more data
add_more_data = st.button("Add More Data")
while add_more_data:
    st.write("Enter test data:")
    date = st.text_input("Date:")
    comment = st.text_input("Comment:")
    Pwf = st.number_input("Flowing bottomhole pressure (bar):")
    Q = st.number_input("Rate (km3/d):")
    data.append((date, comment, Pwf, Q))

    add_more_data = st.button("Add More Data")

# Perform calculations
if st.button("Calculate IPR"):
    # Print data as a table
    st.write("\nInput Data:")
    headers = ["Date", "Comment", "Pwf (bar)", "Rate (km3/d)"]
    st.table(data)

    # Perform calculations
    calculate_IPR(data, Pws)
