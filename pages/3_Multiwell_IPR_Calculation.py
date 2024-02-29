import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

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
    st.title('Multiwell IPR Calculation')

    intro=('''In order to perform the curve fitting for several wells a .csv file needs to be loaded with the folliowing format. 

| Well | Pres (bar) | BHP (bar) | Rate (km3/d) for gas / Rate (m3/d) for oil |
|------|------------|-----------|----------------------------------------------|
|      |            |           |                                              |


*Note that all test data should be referenced to the same reservoir pressure*. ''')

    st.markdown(intro)

    st.divider()

    reservoir_type = st.radio("Select Reservoir Type:", ('Gas', 'Oil'))

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        coefficients_df = calculate_coefficients(data, reservoir_type)

        st.write("Data with IPR coefficients:")
        if reservoir_type == 'Gas':
            coefficients_df_formatted = format_coefficients(coefficients_df)
            st.write(coefficients_df_formatted)
            if st.button("Download Coefficients as CSV"):
                download_csv(coefficients_df_formatted)
        else:  # For Oil reservoir type, no formatting is applied
            st.write(coefficients_df)
            if st.button("Download Coefficients as CSV"):
                download_csv(coefficients_df)


        st.write("## IPR Curves")
        for well_name, well_data in data.groupby("Well"):
            st.write(f"### Well {well_name}")
            if reservoir_type == 'Gas':
                plot_IPR_curve(well_data, coefficients_df[coefficients_df['Well'] == well_name])
            elif reservoir_type == 'Oil':
                plot_Vogel_curve(well_data, coefficients_df[coefficients_df['Well'] == well_name])

def format_coefficients(coefficients_df):
    coefficients_df_formatted = coefficients_df.copy()
    coefficients_df_formatted['a (bar2/(m3/d)2)'] = coefficients_df['a (bar2/(m3/d)2)'].apply(lambda x: f'{x:.2e}')
    coefficients_df_formatted['b (bar2/m3/d)'] = coefficients_df['b (bar2/m3/d)'].apply(lambda x: f'{x:.2e}')
    return coefficients_df_formatted

def download_csv(dataframe):
    csv = dataframe.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='coefficients.csv',
        mime='text/csv')

def plot_IPR_curve(data, coefficients):
    well_name = data["Well"].iloc[0]
    Pws = data["Pres (bar)"].iloc[0]
    a = coefficients['a (bar2/(m3/d)2)'].values[0] * 1e6
    b = coefficients['b (bar2/m3/d)'].values[0] * 1000
    AOF = coefficients['AOF (km3/d)'].values[0]

    Q_range = np.linspace(0, AOF, 500)
    Pwf_fit = curve_IPR(Q_range, [a, b, Pws])

    fig, ax = plt.subplots()
    ax.plot(Q_range, Pwf_fit, color='blue', label=f'IPR Curve - Well {well_name}')
    ax.scatter(data["Rate (km3/d)"], data["BHP (bar)"], color='magenta', label=f'Test Data - Well {well_name}')

    ax.set_xlabel('Rate (km$^3$/d)')
    ax.set_ylabel('Pressure (bar)')
    ax.set_title(f'Test Data and IPR Curves for Well {well_name}')
    ax.legend()
    ax.grid(True)
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)

    st.pyplot(fig)

def plot_Vogel_curve(data, coefficients):
    well_name = data["Well"].iloc[0]
    Pws = data["Pres (bar)"].iloc[0]
    Qmax = coefficients['Qmax (m3/d)'].values[0]

    Pwf_range = np.linspace(0, Pws, 500)
    Qmax_curve_fit = curve_IPR_Vogel(Pwf_range, Pws, Qmax)

    fig, ax = plt.subplots()
    ax.plot(Qmax_curve_fit, Pwf_range, color='black', label='IPR (Fitted Curve)')
    ax.scatter(data["Rate (m3/d)"], data["BHP (bar)"], color='magenta', label='Test Data')

    ax.set_xlabel('Rate (m$^3$/d)')
    ax.set_ylabel('Pressure (bar)')
    ax.set_title(f'Pressure vs Rate for Well {well_name}')
    ax.legend()
    ax.grid(True)
    ax.set_xlim(0, ax.get_xlim()[1])
    ax.set_ylim(0, ax.get_ylim()[1])

    st.pyplot(fig)

if __name__ == "__main__":
    main()
