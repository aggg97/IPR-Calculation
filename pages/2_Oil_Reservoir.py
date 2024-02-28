import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import pandas as pd

st.title("Oil Reservoir")

st.header("Vogel Reservoir Model:")


st.write("Vogel's IPR quadratic equation is defined as: ")


st.latex( r''' \frac{Q}{AOF}= 1-0.2\frac{Pwf}{Pws}-0.8\left(\frac{Pwf}{Pws}\right)^{2}''')

st.latex(r'''(Q= AOF \cdot \left[1-0.2\frac{Pwf}{Pws}-0.8\left(\frac{Pwf}{Pws}\right)^{2}\right]''')

st.divider()

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

    return data

def main():
    # Load test data
    data = collect_data()

    if data:
        # Convert data into DataFrame
        data_df = pd.DataFrame(data, columns=["Date", "Comment", "Pwf (bar)", "Rate (km3/d)"])

        # Extract Pws
        Pws = data_df.loc[0, "Pwf (bar)"]

        # Add a data point where rate q = 0 and Pwf = Pws
        new_row = {'Date': 'Initial', 'Comment': 'Initial condition', 'Pwf (bar)': Pws, 'Rate (km3/d)': 0}
        data_df = data_df.append(new_row, ignore_index=True)

        # Error function to minimize
        def error_function(Qmax, Pwf, Q, Pws):
            predicted_Q = curve_IPR_Vogel(Pwf, Pws, Qmax)
            errors = np.log(predicted_Q) - np.log(Q)
            squared_errors = np.sum(errors ** 2)
            scaled_squared_errors = squared_errors * 1000
            return scaled_squared_errors

        # Perform optimization
        initial_guess = 100  # Initial guess for Qmax
        bounds = [(0, np.inf)]  # Define bounds for Qmax
        result = minimize(error_function, initial_guess, args=(data_df["Pwf (bar)"], data_df["Rate (km3/d)"], Pws), bounds=bounds)

        # Extract optimized parameter
        Qmax_fit = result.x[0]

        st.header("Fitted Parameters:")
        st.metric(label="Qmax (Sm3/d)", value=f"{Qmax_fit:.2f}")

        # Generate curve points for plotting
        Pwf_range = np.linspace(0, min(np.max(data_df["Pwf (bar)"]), Pws), 500)
        Qmax_curve_fit = curve_IPR_Vogel(Pwf_range, Pws, Qmax_fit)

        # Plot test points
        plt.scatter(data_df["Rate (km3/d)"], data_df["Pwf (bar)"], color='red', label='Reservoir Pressure and Test Data')

        # Plot fitted curve
        plt.plot(Qmax_curve_fit, Pwf_range, color='blue', label='Fitted Curve')

        # Set the limits for both x and y axes
        plt.xlim(0, plt.xlim()[1])
        plt.ylim(0, plt.ylim()[1])

        plt.xlabel('Rate (km$^3$/d)')
        plt.ylabel('Pressure (bar)')
        plt.title('Pressure vs Rate')
        plt.legend()
        plt.grid(True)

        st.pyplot()

    else:
        st.write("No data provided.")

def curve_IPR_Vogel(Pwf, Pws, Qmax):
    return Qmax * (1 - 0.2 * (Pwf / Pws) - 0.8 * (Pwf / Pws) ** 2)

if __name__ == "__main__":
    main()

st.divider()
error=("""**Error function to minimize by solver during curve fitting:
$ ∑ [ln(AOF*[1-0.2\frac{Pwf}{Pws}-0.8(\frac{Pwf}{Pws})^{2}]) -  ln( Q)]^2\cdot 1000 $**

*NOTE: By taking the logarithm of the difference between the model prediction and the test data,
we can effectively handle a wide range of values and mitigate the influence of outliers.
Squaring the differences ensures that all values are positive, 
facilitating optimization algorithms to converge efficiently. 
Additionally, multiplying the squared differences
by a large number amplifies their impact during optimization, 
improving the precision of the solver and enabling finer adjustments to the model parameters.*""")

st.markdown(error)

st.divider()
