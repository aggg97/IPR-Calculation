import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from tabulate import tabulate

# Definition of the quadratic curve equation (Inflow Performance Relationship - IPR)
def curve_IPR(Q, a, b, Pws):
    return np.sqrt(-a * Q ** 2 - b * Q + Pws**2)

# Function to collect input data
def collect_data():
    st.subheader("Input Test Data")
    rows = st.number_input("Number of Test Data", min_value=1, value=1)
    Pws = st.number_input("Reservoir Pressure (Pws) (bar)")

    # Create an empty list to store input values
    data = []

    for i in range(rows):
        st.write(f"### Test Data {i+1}")
        col1, col2 = st.columns(2)
        with col1:
            date = st.text_input("Date", key=f"date_{i}")
            Pwf = st.number_input("Flowing Bottomhole Pressure (Pwf) (bar)", key=f"Pwf_{i}")
        with col2:
            comment = st.text_input("Comment", key=f"comment_{i}")
            Q = st.number_input("Rate (Q) (km3/d)", key=f"Q_{i}")

        data.append((date, comment, Pwf, Q))

    # Print data as a table
    st.subheader("Input Data Summary")
    headers = ["Date", "Comment", "Pwf (bar)", "Rate (km3/d)"]
    st.write(tabulate(data, headers=headers, tablefmt="grid"))

    return Pws, data

def main():
    st.title("IPR Curve Fitting")

    # Collect test data
    Pws, data = collect_data()

    # Convert data into arrays
    Q_data = np.array([d[3] for d in data])
    P_data = np.array([d[2] for d in data])

    # Perform curve fitting
    initial_guess = [3.75e-9, 4.17e-4]  # Initial guess for the parameters a, b, and c
    bounds = ([0, 0], [np.inf, np.inf])  # Bounds for the parameters
    params, _ = curve_fit(curve_IPR, Q_data, P_data, p0=initial_guess, bounds=bounds)
    a_fit, b_fit = params

    st.write("Fitted Parameters:")
    st.write(f"a: {a_fit:2e} bar2/(Sm3/day)2")
    st.write(f"b: {b_fit:2e} bar2/(Sm3/day)")

    # Range of points for extrapolation of the curve
    Q_range = np.linspace(0, np.max(Q_data), 500)
    Pwf_fit = curve_IPR(Q_range, a_fit, b_fit, Pws)  # Assuming constant Pws for simplicity

    # Plot
    st.subheader("IPR Curve")
    fig, ax = plt.subplots()
    ax.scatter(Q_data, P_data, color='red', label='Test Data')
    ax.plot(Q_range, Pwf_fit, color='blue', label='Fitted Curve')
    ax.set_xlabel('Rate (km$^3$/ d)')
    ax.set_ylabel('Pressure (bar)')
    ax.set_title('Pressure vs Rate')
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

if __name__ == "__main__":
    main()
