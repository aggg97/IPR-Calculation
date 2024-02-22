import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from tabulate import tabulate

st.title("IPR Calculation")
st.header("Forcheimer Reservoir Model: ")
forcheimer= ('''The Forcheimer equation expresses the inflow performance in terms of turbulent and non turbulent pressure drop coefficients expressed as:

*   "a"         the turbulent pressure drop (Non-Darcy Coefficient )
*   "b"         the laminar pressure drop (Non-Darcy Coefficient)


To represent the IPR in a Pressure vs Rate plot then,

$\Delta P^2 = Pws ^2- Pwf^2 = a \cdot Q^2 + b \cdot Q $


$a \cdot Q^2 + b \cdot Q  - (Pws ^2- Pwf^2 ) = 0$


$a \cdot Q^2 + b \cdot Q  - Pws ^2 + Pwf^2 =0 $


$Pwf=\sqrt{Pws ^2-a \cdot Q^2 -b \cdot Q }$
''')

st.markdown(forcheimer)

Pwf = st.number_input("Enter reservoir pressure (in bar): ")

st.header("Enter test data: ")
date = st.date_input("Enter date: ")
comment = st.text_input("Enter comment: ")
Pwf = st.number_input("Enter flowing bottomhole pressure (in bar): ")
Q = st.number_input("Enter rate (in km3/d): ")

st.button("Calculate IPR for test data")
# Definition of the quadratic curve equation (Inflow Performance Relationship - IPR)
def curve_IPR(Q, a, b):
    Pws = data[0][2]
    return np.sqrt(-a * Q ** 2 - b * Q + Pws**2)

# Function to collect input data
def collect_data():
    data = []
    Pws = float(input("Enter reservoir pressure (in bar): "))
    Q=0
    while True:
        data.append((date, comment, Pws, Pwf, Q))

# Collect test data
data= collect_data()

# Convert rate from km3/d to Sm3/day
for i in range(len(data)):
    data[i] = (data[i][0], data[i][1], data[i][2], data[i][3], data[i][4] * 1e3)
print(data)
print (data[0][2])
Pws=data[0][2]

# For Pws
data2 = [(Pws,0)]
print(data2)

# Convert data into arrays
Q_data = np.array([d[4] for d in data]+[d[1] for d in data2])
P_data = np.array([d[3] for d in data]+[d[0] for d in data2])




# Perform curve fitting
initial_guess = [3.75e-9, 4.17e-4]  # Initial guess for the parameters a, b, and c
bounds = ([0, 0], [np.inf, np.inf])  # Bounds for the parameters
params, _ = curve_fit(curve_IPR, Q_data,P_data,p0=initial_guess, bounds=bounds)
a_fit, b_fit = params

print("")
print("")
print("Fitted Parameters:")
print(f"a: {a_fit} bar2/(Sm3/day)2")
print(f"b: {b_fit} bar2/(Sm3/day)")
print(f"Reservoir Pressure: {Pws} bar")
print("")
print("")

# AOF Calculation
# Bhaskara’s formula to find positive root
discriminant = b_fit ** 2 + 4 * a_fit * Pws ** 2
if discriminant >= 0:
    AOF = (-b_fit + np.sqrt(discriminant)) / (2 * a_fit)
    print(f"AOF: {AOF/1000} km3/d")
else:
    print("No real roots exist.")


# Range of points for extrapolation of the curve
Q_range = np.linspace(0, AOF, 500)
Pwf_fit = curve_IPR(Q_range, a_fit, b_fit)

# Test points
plt.scatter(Q_data / 1000, P_data, color='red', label='Reservoir Pressure and Test Data ')

# Fitted curve
plt.plot(Q_range / 1000, Pwf_fit, color='blue', label='Fitted Curve')

# Set the limits for both x and y axes
plt.xlim(0, plt.xlim()[1])  # x-axis minimum to 0
plt.ylim(0, plt.ylim()[1])  # y-axis minimum to 0

plt.xlabel('Rate (km$^3$/ d)')
plt.ylabel('Pressure (bar)')
plt.title('Pressure vs Rate')
plt.legend()
plt.grid(True)
plt.show()

st.pyplot(plt)

st.markdown("ahora hay que ver como incorporar muchos tests... se podria poner un boton add test data y que te de las ventanas para cargar datos... algo asi...y como hacer para darle play al codigo que hace la IPR y vincular todo con lo anterior")

