import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Definition of the quadratic curve equation (Inflow Performance Relationship - IPR)
def curve_IPR(Q, params):
    a, b, Pws = params
    return np.sqrt(-a * Q ** 2 - b * Q + Pws ** 2)

# Definition of the curve equation (Vogel IPR)
def curve_IPR_Vogel(Pwf, Pws, Qmax):
    return Qmax * (1 - 0.2 * (Pwf / Pws) - 0.8 * (Pwf / Pws) ** 2)

# Error function to minimize for quadratic IPR
def error_function(params, data):
    Q = data["Rate (km3/d)"]
    Pwf = data["BHP (bar)"]
    Pws = data["Pres (bar)"]
    a, b, Pws = params
    errors = np.log(np.abs(Pws ** 2 - a * Q ** 2 - b * Q)) - np.log(np.abs(Pwf ** 2))
    squared_errors = np.sum(errors ** 2)
    scaled_squared_errors = squared_errors * 1000
    return scaled_squared_errors

# Error function to minimize for Vogel IPR
def error_function_vogel(params, Pwf, Q, Pws):
    Qmax = params[0]
    predicted_Q = curve_IPR_Vogel(Pwf, Pws, Qmax)
    errors = np.log(predicted_Q) - np.log(Q)
    squared_errors = np.sum(errors ** 2)
    scaled_squared_errors = squared_errors * 1000
    return scaled_squared_errors

# Calculate coefficients for each well
def calculate_coefficients(data, reservoir_type):
    coefficients_list = []

    for index, well_data in data.groupby("Well"):
        Pws = well_data["Pres (bar)"].iloc[0]

        if reservoir_type == 'Gas':
            initial_guess = [1.65e-2, 4.17e-1, Pws]  # Initial guess for optimization
            bounds = [(0, np.inf), (0, np.inf), (Pws - 1e-9, Pws + 1e-9)]  # Bounds for parameters
            result = minimize(error_function, initial_guess, args=(well_data,), bounds=bounds)

            a_fit, b_fit, Pws_fit = result.x
            discriminant = b_fit ** 2 + 4 * a_fit * Pws_fit ** 2
            if discriminant >= 0:
                AOF = (-b_fit + np.sqrt(discriminant)) / (2 * a_fit)
            else:
                AOF = np.nan

            coefficients_list.append({
                'Well': index,
                'Pres (bar)': Pws,
                'a (bar2/(m3/d)2)': result.x[0] / 1e6,
                'b (bar2/m3/d)': result.x[1] / 1000,
                'AOF (km3/d)': AOF
            })

        elif reservoir_type == 'Oil':
            initial_guess = [10]  # Initial guess for Qmax
            bounds = [(0, np.inf)]  # Define bounds for Qmax
            result = minimize(error_function_vogel, initial_guess, args=(well_data["BHP (bar)"], well_data["Rate (m3/d)"], Pws), bounds=bounds)

            Qmax_fit = result.x[0]

            coefficients_list.append({
                'Well': index,
                'Pres (bar)': Pws,
                'Qmax (m3/d)': Qmax_fit
            })

    # Convert list of dictionaries to DataFrame
    coefficients_df = pd.DataFrame(coefficients_list)

    return coefficients_df

def main():
    st.title('Reservoir IPR Analysis')

    reservoir_type = st.radio("Select Reservoir Type:", ('Gas', 'Oil'))

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        coefficients_df = calculate_coefficients(data, reservoir_type)
        st.write("Data with IPR coefficients:")
        st.write(coefficients_df.applymap(lambda x: f'{x:.2e}' if isinstance(x, (int, float)) else x))

        st.write("## IPR Curves")
        for well_name, well_data in data.groupby("Well"):
            st.write(f"### Well {well_name}")
            if reservoir_type == 'Gas':
                plot_IPR_curve(well_data, coefficients_df[coefficients_df['Well'] == well_name])
            elif reservoir_type == 'Oil':
                plot_Vogel_curve(well_data, coefficients_df[coefficients_df['Well'] == well_name])


def plot_IPR_curve(data, coefficients):
    well_name = data["Well"].iloc[0]
    Pws = data["Pres (bar)"].iloc[0]
    a = coefficients['a (bar2/(m3/d)2)'].values[0] * 1e6
    b = coefficients['b (bar2/m3/d)'].values[0] * 1000
    AOF = coefficients['AOF (km3/d)'].values[0]

    Q_range = np.linspace(0, AOF, 500)
    Pwf_fit = curve_IPR(Q_range, [a, b, Pws])

    plt.plot(Q_range, Pwf_fit, color='blue', label=f'IPR Curve - Well {well_name}')

    plt.scatter(data["Rate (km3/d)"], data["BHP (bar)"], color='magenta', label=f'Test Data - Well {well_name}')

    plt.xlabel('Rate (km$^3$/d)')
    plt.ylabel('Pressure (bar)')
    plt.title(f'Test Data and IPR Curves for Well {well_name}')
    plt.legend()
    plt.grid(True)
    plt.xlim(0, None)
    plt.ylim(0, None)
    st.pyplot()

def plot_Vogel_curve(data, coefficients):
    well_name = data["Well"].iloc[0]
    Pws = data["Pres (bar)"].iloc[0]
    Qmax = coefficients['Qmax (m3/d)'].values[0]

    Pwf_range = np.linspace(0, Pws, 500)
    Qmax_curve_fit = curve_IPR_Vogel(Pwf_range, Pws, Qmax)

    plt.plot(Qmax_curve_fit, Pwf_range, color='black', label='IPR (Fitted Curve)')

    plt.scatter(data["Rate (m3/d)"], data["BHP (bar)"], color='magenta', label='Test Data')

    plt.xlabel('Rate (m$^3$/d)')
    plt.ylabel('Pressure (bar)')
    plt.title(f'Pressure vs Rate for Well {well_name}')
    plt.legend()
    plt.grid(True)
    plt.xlim(0, plt.xlim()[1])
    plt.ylim(0, plt.ylim()[1])
    st.pyplot()

if __name__ == "__main__":
    main()
