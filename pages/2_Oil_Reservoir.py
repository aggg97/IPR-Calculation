import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import pandas as pd

st.page_link("Homepage.py", label="Go back to Homepage")
st.title("Oil Reservoir")

st.header("Vogel Reservoir Model:")


st.write("Vogel's IPR quadratic equation is defined as: ")


st.latex( r''' \frac{Q}{AOF}= 1-0.2\frac{Pwf}{Pws}-0.8\left(\frac{Pwf}{Pws}\right)^{2}''')

st.latex(r'''(Q= AOF \cdot \left[1-0.2\frac{Pwf}{Pws}-0.8\left(\frac{Pwf}{Pws}\right)^{2}\right]''')

st.divider()

# Definition of the curve equation (Vogel IPR)
def curve_IPR_Vogel(Pwf, Pws, Qmax):
    return Qmax * (1 - 0.2 * (Pwf / Pws) - 0.8 * (Pwf / Pws)**2)
    
# Function to collect input data
def collect_data():
    st.header("Input Test Data")
    rows = st.number_input("Number of Test Data", min_value=1, value=1)

    # Create an empty list to store input values
    data = []
    Pws = st.number_input("Reservoir pressure (in bar)", value=0.0)

    for i in range(rows):
        st.write(f"### Test Data {i+1}")
        date = st.date_input("Date", key=f"date_{i}")
        comment = st.text_input("Comment", key=f"comment_{i}")
        Pwf = st.number_input("Flowing Bottomhole Pressure (bar)", key=f"Pwf_{i}")
        Q = st.number_input("Rate (m3/d)", key=f"Q_{i}")

        data.append([date, comment, Pws, Pwf, Q])

    return pd.DataFrame(data, columns=["Date", "Comment", "Pws (bar)", "Pwf (bar)", "Rate (m3/d)"])

def main():
    # Load test data
    data = collect_data()

    if not data.empty:
        # Extract Pws
        Pws = data.loc[0, "Pws (bar)"]

        # Add a data point where rate q = 0 and Pwf = Pws
        new_row = {'Date': 'Initial', 'Comment': 'Initial condition', 'Pws (bar)': Pws, 'Pwf (bar)': Pws, 'Rate (km3/d)': 0}
        data = data.append(new_row, ignore_index=True)

        # Error function to minimize
        def error_function(params, Pwf, Q, Pws):
            Qmax = params[0]
            predicted_Q = curve_IPR_Vogel(Pwf, Pws, Qmax)
            errors = np.log(predicted_Q) - np.log(Q)
            squared_errors = np.sum(errors ** 2)
            scaled_squared_errors = squared_errors * 1000
            return scaled_squared_errors
        
        # Perform optimization
        initial_guess = [100]  # Initial guess for Qmax
        bounds = [(0, np.inf)]  # Define bounds for Qmax
        result = minimize(error_function, initial_guess, args=(data["Pwf (bar)"], data["Rate (Sm3/d)"], Pws), bounds=bounds)

        # Extract optimized parameter
        Qmax_fit = result.x[0]
        st.header("AOF (m3/d):")
        st.write(Qmax_fit)

        # Generate curve points for plotting
        Pwf_range = np.linspace(0, min(np.max(data["Pwf (bar)"]), Pws), 500)
        Qmax_curve_fit =curve_IPR_Vogel(Pwf_range, Pws, Qmax_fit)
        
        # Plot
        st.subheader("IPR Plot")
        fig, ax = plt.subplots()
        ax.scatter(data["Rate (m3/d)"], data["Pwf (bar)"], color='red', label='Pres and Test Data') # corrected scatter plot arguments
        ax.plot(Qmax_curve_fit, Pwf_range, color='blue', label='IPR (Fitted Curve)')
        ax.set_xlabel('Rate (m$^3$/ d)')
        ax.set_ylabel('Pressure (bar)')
        ax.set_title('Pressure vs Rate')
        ax.legend()
        ax.grid(True)
        
        # Set the limits of the axes to ensure the plot starts at (0, 0)
        ax.set_xlim(left=0)  # Setting only the left limit to 0
        ax.set_ylim(bottom=0) # Setting only the bottom limit to 0
        
        st.pyplot(fig)


if __name__ == "__main__":
    main()
    
st.divider()
st.write("Error function to minimize by solver during curve fitting:")

st.latex(r''' ∑ [ln(AOF*[1-0.2\frac{Pwf}{Pws}-0.8(\frac{Pwf}{Pws})^{2}]) -  ln( Q)]^2\cdot 1000 ''')

st.write('''*NOTE: By taking the logarithm of the difference between the model prediction and the test data, 
we can effectively handle a wide range of values and mitigate the influence of outliers. 
Squaring the differences ensures that all values are positive, facilitating optimization algorithms
to converge efficiently. Additionally, multiplying the squared differences by a large number amplifies their impact during optimization, 
improving the precision of the solver and enabling finer adjustments to the model parameters*''')

st.divider()
st.set_option('depreciation.showPyplotGlobalUse',False)
