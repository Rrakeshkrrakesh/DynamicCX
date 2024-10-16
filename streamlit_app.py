import streamlit as st
import pandas as pd
import json

# Load the JSON data
file_path = 'CX_Dynamic_Layouts_Config.json'  # Replace with your actual JSON file path
with open(file_path) as f:
    data = json.load(f)

# Sidebar for user input
selected_sheet = st.sidebar.selectbox("Select User Type, Fuel & Meter Type", list(data.keys()))

# Convert selected sheet data to DataFrame
df = pd.DataFrame(data[selected_sheet])

# Debug: Print the column names to identify any issues
st.write("Available columns:", df.columns)

# Rename columns if necessary (based on actual column names)
if 'Widget/Page' in df.columns:
    df = df.rename(columns={'Widget/Page': 'Widget Name'})

# Ensure 'Widget Name' column exists
if 'Widget Name' not in df.columns:
    st.error("The 'Widget Name' column is missing.")
else:
    # Proceed with the app logic
    def get_applicable_widgets(df, attributes):
        """Get applicable widgets based on attributes and widget status."""
        if not attributes:
            return df[df['Status (if applicable)'] != 'OFF']['Widget Name'].tolist()

        applicable_widgets = []
        for _, row in df.iterrows():
            widget = row['Widget Name']
            if row['Status (if applicable)'] == 'OFF':
                continue

            is_applicable = any(
                attr in df.columns and pd.notna(row[attr]) and row[attr] != 0
                for attr in attributes
            )
            if is_applicable:
                applicable_widgets.append(widget)
        return applicable_widgets

    # Display the DataFrame
    st.dataframe(df)
