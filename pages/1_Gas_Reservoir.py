import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from tabulate import tabulate
import pandas as pd

st.page_link("Homepage.py", label="Go back to Homepage")
st.title("Gas Reservoir")

st.header("Forcheimer Reservoir Model: ")

forcheimer = ('The Forcheimer equation expresses the inflow performance in terms of turbulent and non-turbulent pressure drop coefficients expressed as:\n\n'
              '*   "a"         the turbulent pressure drop (Non-Darcy Coefficient )\n'
              '*   "b"         the laminar pressure drop (Non-Darcy Coefficient)\n\n'
              'To represent the IPR in a Pressure vs Rate plot then, ')

st.markdown(forcheimer)

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
    Pws = st.number_input("Reservoir pressure (in bar)", value=0.0)

    for i in range(rows):
        st.write(f"### Test Data {i+1}")
        date = st.date_input("Date", key=f"date_{i}")
        comment = st.text_input("Comment", key=f"comment_{i}")
        Pwf = st.number_input("Flowing Bottomhole Pressure (bar)", key=f"Pwf_{i}")
        Q = st.number_input("Rate (km3/d)", key=f"Q_{i}")

        data.append([date, comment, Pws, Pwf, Q])

    return pd.DataFrame(data, columns=["Date", "Comment", "Pws (bar)", "Pwf (bar)", "Rate (km3/d)"])

def main():
    # Load test data
    data = collect_data()

    if not data.empty:
        # Extract Pws
        Pws = data.loc[0, "Pws (bar)"]

        # Extract Pwf and Q data
        Pwf_data = data["Pwf (bar)"]
        Q_data = data["Rate (km3/d)"]

        # Define error function to minimize
        def error_function(params):
            a, b, Pws = params
            errors = np.log(np.abs(Pws ** 2 - a * Q_data ** 2 - b * Q_data)) - np.log(np.abs(Pwf_data ** 2))
            squared_errors = np.sum(errors ** 2)
            scaled_squared_errors = squared_errors * 1000
            return scaled_squared_errors

        # Perform optimization
        initial_guess = [1.65e-2, 4.17e-1, Pws]  #this units are in bar2/km3/d
        bounds = [(0, np.inf), (0, np.inf), (Pws - 1e-9, Pws + 1e-9)]
        result = minimize(error_function, initial_guess, bounds=bounds)

        # Extract optimized parameters
        a_fit, b_fit, Pws_fit = result.x

        st.header("Fitted Parameters:")
        col1, col2 = st.columns(2)
        col1.metric(label=f":red[a (bar2/(Sm3/day)2)]", value=f"{a_fit/1e6:.2e}")
        col1.metric(label=f":green[b (bar2/Sm3/day)]", value=f"{b_fit/1e3:.2e}")
        col2.metric(label=f":black[Reservoir Pressure (bar)]", value=f"{Pws_fit:.2f}")

        # AOF Calculation
        discriminant = b_fit ** 2 + 4 * a_fit * Pws_fit ** 2
        if discriminant >= 0:
            AOF = (-b_fit + np.sqrt(discriminant)) / (2 * a_fit)
            col2.metric(label=f":blue[AOF (km3/d)]", value=f"{AOF:.2f}")
        else:
            st.write("No real roots exist.")

        # Range of points for extrapolation of the curve
        Q_range = np.linspace(0, AOF, 500)
        Pwf_fit = curve_IPR(Q_range, [a_fit, b_fit, Pws_fit])

        # Plot
        st.subheader("IPR Plot")
        fig, ax = plt.subplots()
        ax.scatter(Q_data, Pwf_data, color='red', label='Test Data')
        ax.plot(Q_range, Pwf_fit, color='blue', label='IPR (Fitted Curve)')
        ax.set_xlabel('Rate (km$^3$/ d)')
        ax.set_ylabel('Pressure (bar)')
        ax.set_title('Pressure vs Rate')
        ax.legend()
        ax.grid(True)

        # Set the limits of the axes to ensure the plot starts at (0, 0)
        ax.set_xlim(left=0, auto=True)
        ax.set_ylim(bottom=0, auto=True)

        st.pyplot(fig)

        st.divider()
      
        st.write("Error function to minimize by solver during curve fitting: ")
        
        st.latex(r''' ∑ [ln(Pws^2 - a \cdot Q^2 - b \cdot Q  ) -  ln( Pwf^2)]^2\cdot 1000 ''')
        
        st.write('''*NOTE: By taking the logarithm of the difference between the model prediction and the test data, 
        we can effectively handle a wide range of values and mitigate the influence of outliers. 
        Squaring the differences ensures that all values are positive, facilitating optimization algorithms
        to converge efficiently. Additionally, multiplying the squared differences by a large number amplifies their impact during optimization, 
        improving the precision of the solver and enabling finer adjustments to the model parameters.*''')
        
        st.divider()
        
        st.subheader("Reservoir Pressure Sensitivity - Fetkovich Method")

        st.write("For gas: ")
        st.latex(r'''\frac{𝜇_b. 𝑍_𝑏}{𝜇_𝑎. 𝑍_𝑎}≈ 1''')
    
        st.latex(r'''\frac{AOF_a}{AOF_b} = \frac{(Pws_a)^{2n}}{(Pws_b)^{2n}}''')
      
        st.write("where n is a a value between 0.5-1 (depending if laminar or turbulent flow)")
      
        st.write("*NOTE: It is important to remember that the IPR maintains its shape (a, b coefficients don't change). Only its extreme values change (Reservoir presure and AOF)*")

        # Collect new reservoir pressure
        Pws_new = st.number_input("Enter new reservoir pressure (in bar) to model IPR evolution: ", value=0.0)
        
        # Fetkovich Method
        n = 0.5
        AOF_or=AOF
        Pws_or=Pws
        
        def calculate_AOF_new(AOF_or, Pws_or, Pws_new, n):
            AOF_new = AOF_or * (Pws_new / Pws_or) ** (2 * n)
            return AOF_new
        
        # Future IPR
        def curve_IPR_future(Q, a, b, Pws_new):
            return np.sqrt(-a * Q ** 2 - b * Q + Pws_new ** 2)
        
        # Calculate new AOF
        AOF_new = calculate_AOF_new(AOF, Pws, Pws_new, n)
        st.write("")
        st.write(f"AOF: {AOF_new:.2f} km3/d when reservoir pressure is {Pws_new} bar")
        
        # Range of points for extrapolation of the future curve
        Q_range_or = np.linspace(0, AOF_or, 500)
        Q_range_new = np.linspace(0, AOF_new, 500)
        Pwf_fit_new = curve_IPR_future(Q_range_new, a_fit, b_fit, Pws_new)
        
        # Plot
        st.subheader("Future IPR Plot")
        fig, ax = plt.subplots()
        ax.scatter(data["Rate (km3/d)"], data["Pwf (bar)"], color='red', label='Test Data ')
        ax.plot(Q_range_or, Pwf_fit, color='blue', label='IPR (Fitted Curve)')
        ax.plot(Q_range_new, Pwf_fit_new, color='green', linestyle='--', label='IPR Sensitivity')
        ax.set_xlabel('Rate (km$^3$/ d)')
        ax.set_ylabel('Pressure (bar)')
        ax.set_title('Pressure vs Rate')
        ax.legend()
        ax.grid(True)
        ax.set_xlim(0, ax.get_xlim()[1])
        ax.set_ylim(0, ax.get_ylim()[1])
        
        st.pyplot(fig)

    else:
        st.write("No data provided.")

if __name__ == "__main__":
    main()
