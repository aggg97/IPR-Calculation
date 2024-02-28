import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from tabulate import tabulate

st.title("Gas Reservoir")

st.header("Forcheimer Reservoir Model: ")

st.write("The Forcheimer equation expresses the inflow performance in terms of turbulent (a coefficient) and non turbulent (b coefficient) pressure drop coefficients expressed as:")

st.latex(r'''\Delta P^2 = Pws ^2- Pwf^2 = a \cdot Q^2 + b \cdot Q ''')

st.latex(r'''a \cdot Q^2 + b \cdot Q  - (Pws ^2- Pwf^2 ) = 0''')

st.latex(r'''a \cdot Q^2 + b \cdot Q  - Pws ^2 + Pwf^2 =0 ''')

st.latex(r'''Pwf=\sqrt{Pws ^2-a \cdot Q^2 -b \cdot Q }''')


st.divider()

# Definition of the quadratic curve equation (Inflow Performance Relationship - IPR)
def curve_IPR(Q, params):
    a, b, Pws = params
    return np.sqrt(-a * Q ** 2 - b * Q + Pws ** 2)

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

        data.append([date, comment, Pwf, Q])

    return data

def main():
    # Load test data
    data = collect_data()

    if data:
        # Extract Pws
        Pws = data[0][2]

        # Define error function to minimize
        def error_function(params):
            a, b, Pws = params
            errors = np.log(np.abs(Pws ** 2 - a * Q_data ** 2 - b * Q_data)) - np.log(np.abs(Pwf_data ** 2))
            squared_errors = np.sum(errors ** 2)
            scaled_squared_errors = squared_errors * 1000
            return scaled_squared_errors

        # Extract Pwf and Q data
        Pwf_data = np.array([d[2] for d in data])
        Q_data = np.array([d[3] for d in data])

        # Perform optimization
        initial_guess = [3.75e-9, 4.17e-4, Pws]
        bounds = [(0, np.inf), (0, np.inf), (Pws - 1e-9, Pws + 1e-9)]
        result = minimize(error_function, initial_guess, bounds=bounds)

        # Extract optimized parameters
        a_fit, b_fit, Pws_fit = result.x

        st.header("Fitted Parameters:")
        col1, col2 = st.columns(2)
        col1.metric(label=f":red[a (bar2/(Sm3/day)2)]", value=f"{a_fit:.2e}")
        col1.metric(label=f":green[b (bar2/Sm3/day)]", value=f"{b_fit:.2e}")
        col2.metric(label=f":black[Reservoir Pressure (bar)]", value=f"{Pws_fit:.2f}")

        # AOF Calculation
        discriminant = b_fit ** 2 + 4 * a_fit * Pws_fit ** 2
        if discriminant >= 0:
            AOF = (-b_fit + np.sqrt(discriminant)) / (2 * a_fit)
            col2.metric(label=f":blue[AOF (km3/d)]", value=f"{AOF / 1000:.2f}")
        else:
            st.write("No real roots exist.")

        # Range of points for extrapolation of the curve
        Q_range = np.linspace(0, AOF, 500)
        Pwf_fit = curve_IPR(Q_range, [a_fit, b_fit, Pws_fit])

        # Plot
        st.subheader("IPR Curve")
        fig, ax = plt.subplots()
        ax.scatter(Q_data, Pwf_data, color='red', label='Test Data')
        ax.plot(Q_range, Pwf_fit, color='blue', label='Fitted Curve')
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


st.write("Error function to minimize by solver during curve fitting: ")

st.latex(r''' ∑ [ln(Pws^2 - a \cdot Q^2 - b \cdot Q  ) -  ln( Pwf^2)]^2\cdot 1000 ''')

st.write('''*NOTE: By taking the logarithm of the difference between the model prediction and the test data, 
we can effectively handle a wide range of values and mitigate the influence of outliers. 
Squaring the differences ensures that all values are positive, facilitating optimization algorithms
to converge efficiently. Additionally, multiplying the squared differences by a large number amplifies their impact during optimization, 
improving the precision of the solver and enabling finer adjustments to the model parameters*''')

st.divider()

st.divider()
st.sidebar.title("Reservoir Pressure Sensitivity")


