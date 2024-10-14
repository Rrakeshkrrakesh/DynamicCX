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

st.set_page_config(layout="wide")

st.title("Dynamic CX Configuration Matrix")

# Sidebar for dimension selection
st.sidebar.header("Select User Dimensions")
dimension_color_map = {
    'TOU Rate': 'blue',
    'Solar $': 'green',
    'Solar kWh': 'green',
    'EV': 'purple',
    'Budget Billing $': 'orange',
    'Budget Billing kWh': 'orange',
    'AMI': 'red'
}
selected_dimensions = st.sidebar.multiselect("Choose dimensions:", dimensions, 
                                             format_func=lambda dim: f'<span style="color: {dimension_color_map.get(dim, "black")};">{dim}</span>')

# Explanation
if selected_dimensions:
    explanation = f"Based on the selected dimensions ({', '.join(selected_dimensions)}), "
    explanation += "the system determines which elements to include in the user's experience. "
    explanation += "'Include' overrides 'Pass', and 'Kill' overrides both 'Include' and 'Pass'."
else:
    explanation = "Select user dimensions to see how they affect the Dynamic CX configuration."

st.info(explanation)

# Generate table data
table_data = []
for element in elements:
    status = 'pass'
    reason = 'Default pass'
    for dim in selected_dimensions:
        if dim in matrix[element]:
            if matrix[element][dim] == 'kill':
                status = 'kill'
                reason = f'{dim} dimension kills this element'
                break
            elif matrix[element][dim] == 'include':
                status = 'include'
                reason = f'{dim} dimension includes this element'

    table_data.append({
        'Element': element,
        'Status': 'Included' if status == 'include' else 'Not Included',
        'Reason': reason
    })

# Display table
df = pd.DataFrame(table_data)
st.dataframe(df.style.apply(lambda x: ['background: lightgreen' if x.Status == 'Included' else 'background: lightcoral' for i in x], axis=1))

# How it works
st.header("How it works")
st.markdown("""
1. Each element has a default 'pass' status.
2. Dimensions can 'include' or 'kill' an element.
3. 'Include' overrides 'pass'.
4. 'Kill' overrides both 'include' and 'pass'.
5. The final status is determined by evaluating all selected dimensions.
""")

# Dimension Descriptions
st.markdown("**Dimension Descriptions:**")
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

# Display raw matrix data
if st.checkbox("Show raw matrix data"):
    st.json(matrix)
