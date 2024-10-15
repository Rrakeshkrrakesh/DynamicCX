import streamlit as st
import pandas as pd

# Load the Excel file
file_path = 'path_to_your_file/CX_Dynamic_Layouts_Config.xlsx'
xls = pd.ExcelFile(file_path)

# Load the 'Resi_Electric_AMI' sheet (or any other relevant sheet)
resi_electric_ami_df = pd.read_excel(xls, sheet_name='Resi_Electric_AMI')

# Define the configuration matrix (you can modify this to dynamically load from the sheet)
matrix = {
    'Energy Flow': {'Default': 'pass', 'Solar $': 'include', 'Solar kWh': 'include', 'EV': 'pass', 'AMI': 'pass'},
    'Cumulative Balance': {'Default': 'pass', 'Budget Billing $': 'include', 'Budget Billing kWh': 'include'},
    'TOU Usage & Cost': {'Default': 'pass', 'TOU Rate': 'include', 'Solar $': 'kill', 'Solar kWh': 'kill'},
    'Solar Production': {'Default': 'pass', 'Solar $': 'include', 'Solar kWh': 'include'}
}

# Define dimensions
dimensions = ['TOU Rate', 'Solar $', 'Solar kWh', 'EV', 'Budget Billing $', 'Budget Billing kWh', 'AMI']
elements = list(matrix.keys())

# Page layout configuration for Streamlit
st.set_page_config(page_title="CX Configuration Matrix", layout="wide")

# Title and description
st.title("Dynamic CX Configuration Matrix")
st.markdown("""
This tool allows you to visualize how different **user dimensions** influence the inclusion or exclusion of various **elements** 
in the configuration. Based on the selected dimensions, the app dynamically updates the matrix.
""")

# Sidebar for dimension selection
st.sidebar.header("Configure User Dimensions")
dimension_color_map = {
    'TOU Rate': 'blue',
    'Solar $': 'green',
    'Solar kWh': 'green',
    'EV': 'purple',
    'Budget Billing $': 'orange',
    'Budget Billing kWh': 'orange',
    'AMI': 'red'
}

# Using styled dimension names with colors in the sidebar
selected_dimensions = st.sidebar.multiselect(
    "Choose dimensions:",
    dimensions,
    format_func=lambda dim: f'{dim} ({dimension_color_map.get(dim, "black")})'
)

# Display explanation based on user selection
if selected_dimensions:
    explanation = f"Based on the selected dimensions: {', '.join(selected_dimensions)}, "
    explanation += "the system determines whether to include or exclude each element. 'Include' overrides 'Pass', and 'Kill' overrides both."
else:
    explanation = "Please select dimensions from the sidebar to see how they affect the configuration."

st.info(explanation)

# Process the data from the 'Resi_Electric_AMI' sheet (or any other selected sheet)
# This is an example of how to load and process relevant data from the sheet dynamically
# Let's assume the sheet contains columns 'Element', 'Dimension', and 'Status' for now
for index, row in resi_electric_ami_df.iterrows():
    element = row['Element']
    dimension = row['Dimension']
    status = row['Status']  # Could be 'include', 'kill', or 'pass'
    
    if element in matrix:
        matrix[element][dimension] = status

# Generate table data based on the user-selected dimensions
table_data = []
for element in elements:
    status = 'pass'
    reason = 'Default pass'
    for dim in selected_dimensions:
        if dim in matrix[element]:
            if matrix[element][dim] == 'kill':
                status = 'kill'
                reason = f"{dim} dimension kills this element"
                break
            elif matrix[element][dim] == 'include':
                status = 'include'
                reason = f"{dim} dimension includes this element"
    
    table_data.append({
        'Element': element,
        'Status': 'Included' if status == 'include' else 'Not Included',
        'Reason': reason
    })

# Display the results in a formatted table
df = pd.DataFrame(table_data)

st.subheader("Configuration Matrix Result")
st.dataframe(
    df.style.apply(
        lambda x: ['background-color: lightgreen' if x.Status == 'Included' else 'background-color: lightcoral' for i in x], axis=1
    ),
    height=300
)

# How it works section
st.markdown("""
### How it Works:
1. Each element has a default 'pass' status.
2. Dimensions can either 'include' or 'kill' an element.
3. 'Include' overrides the 'pass' status.
4. 'Kill' overrides both 'include' and 'pass'.
5. The final status is determined by evaluating all selected dimensions.
""")

# Option to display raw matrix data
with st.expander("Show raw matrix data"):
    st.json(matrix)
