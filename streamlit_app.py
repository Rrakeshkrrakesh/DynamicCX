import streamlit as st
import pandas as pd

# Define the configuration matrix
matrix = {
    'Energy Flow': {'Default': 'pass', 'Solar $': 'include', 'Solar kWh': 'include', 'EV': 'pass', 'AMI': 'pass'},
    'Cumulative Balance': {'Default': 'pass', 'Budget Billing $': 'include', 'Budget Billing kWh': 'include'},
    'TOU Usage & Cost': {'Default': 'pass', 'TOU Rate': 'include', 'Solar $': 'kill', 'Solar kWh': 'kill'},
    'Solar Production': {'Default': 'pass', 'Solar $': 'include', 'Solar kWh': 'include'}
}

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

# Display dimension descriptions
st.markdown("### Dimension Descriptions")
description_map = {
    'TOU Rate': 'Time-of-use rates impact energy pricing.',
    'Solar $': 'The presence of solar panels affects financial calculations.',
    'Solar kWh': 'The amount of solar energy produced impacts usage patterns.',
    'EV': 'Electric vehicle charging impacts energy consumption.',
    'Budget Billing $': 'Budget billing influences payment schedules.',
    'Budget Billing kWh': 'Budget billing affects usage targets.',
    'AMI': 'Advanced metering infrastructure provides detailed energy usage data.'
}

for dim in dimensions:
    st.markdown(f"- **{dim}:** {description_map.get(dim, 'Description not available.')}")

# Option to display raw matrix data
with st.expander("Show raw matrix data"):
    st.json(matrix)
