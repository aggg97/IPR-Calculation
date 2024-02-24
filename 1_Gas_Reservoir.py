import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from tabulate import tabulate

st.title("Inflow Performance Curve (IPR) Calculation")

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
st.divider()

# Definition of the quadratic curve equation (Inflow Performance Relationship - IPR)
def curve_IPR(Q, a, b):
    return np.sqrt(-a * Q ** 2 - b * Q + Pws**2)

Pws = st.number_input("Reservoir Pressure (bar)")
# Function to collect input data
def collect_data():
    st.header("Input Test Data")
    rows = st.number_input("Number of Test Data", min_value=1, value=1)


    # Create an empty list to store input values
    data = []

    for i in range(rows):
        st.write(f"### Test Data {i+1}")
        date = st.date_input("Date", key=f"date_{i}")
        comment = st.text_input("Comment", key=f"comment_{i}")
        Pwf = st.number_input("Flowing Bottomhole Pressure (bar)", key=f"Pwf_{i}")
        Q = st.number_input("Rate (km3/d)", key=f"Q_{i}")

        data.append((date, comment, Pwf, Q))

    return Pws, data

def main():


    # Load test data
    Pws, data = collect_data()

    if data:
        if st.button('Run IPR Curve Fitting'):
            # Convert rate from km3/d to Sm3/day
            for i in range(len(data)):
                data[i] = (data[i][0], data[i][1], data[i][2],  data[i][3] * 1e3)

            # For Pws
            data2 = [(Pws,0)]
            
            # Convert data into arrays
            Q_data = np.array([d[3] for d in data]+[d[1] for d in data2])
            P_data = np.array([d[2] for d in data]+[d[0] for d in data2])

            # Perform curve fitting
            initial_guess = [3.75e-9, 4.17e-4]  # Initial guess for the parameters a, b, and c
            bounds = ([0, 0], [np.inf, np.inf])  # Bounds for the parameters
            params, _ = curve_fit(curve_IPR, Q_data, P_data, p0=initial_guess, bounds=bounds)
            a_fit, b_fit = params
            
            st.header("Fitted Parameters:")
            col1, col2 = st.columns(2)
            col1.metric(label=f":red[a (bar2/(Sm3/day)2)]", value=f"{a_fit:.2e}")
            col1.metric(label=f":green[b (bar2/Sm3/day)]", value=f"{a_fit:.2e}")
            col2.metric(label=f":black[Reservoir Pressure (bar)]", value=f"{Pws:.2f}")


            # AOF Calculation
            # Bhaskara’s formula to find positive root
            discriminant = b_fit ** 2 + 4 * a_fit * Pws ** 2
            if discriminant >= 0:
                AOF = (-b_fit + np.sqrt(discriminant)) / (2 * a_fit)
                col2.metric(label=f":blue[AOF (km3/d)]",value=f"{AOF/1000:.2f}")
            else:
                st.write("No real roots exist.")
            
            # Range of points for extrapolation of the curve
            Q_range = np.linspace(0, AOF, 500)
            Pwf_fit = curve_IPR(Q_range, a_fit, b_fit)

            # Plot
            st.subheader("IPR Curve")
            fig, ax = plt.subplots()
            ax.scatter(Q_data/1000, P_data, color='red', label='Test Data')
            ax.plot(Q_range/1000, Pwf_fit, color='blue', label='Fitted Curve')
            ax.set_xlabel('Rate (km$^3$/ d)')
            ax.set_ylabel('Pressure (bar)')
            ax.set_title('Pressure vs Rate')
            ax.legend()
            ax.grid(True)

            # Set the limits of the axes to ensure the plot starts at (0, 0)
            ax.set_xlim(left=0, auto=True)
            ax.set_ylim(bottom=0, auto=True)

            st.pyplot(fig)

    

    else:
        st.write("No data provided.")

if __name__ == "__main__":
    main()
