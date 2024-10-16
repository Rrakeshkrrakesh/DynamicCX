import streamlit as st
import pandas as pd
import json

# Load the JSON data
file_path = 'CX_Dynamic_Layouts_Config.json'  # Replace with your actual JSON file path
with open(file_path) as f:
    data = json.load(f)

# Define user attributes and their order of precedence
user_attributes = ['EV', 'TOU', 'Solar', 'Budget Billing', 'Demand Charge', 'Regular']

# Define section order
section_order = [
    "Last month",
    "Current month",
    "Insights & trends",
    "Promotions",
    "Carbon Footprint",
]

# Streamlit app configuration
st.set_page_config(page_title="CX Dynamic Layout Configuration", layout="wide")
st.title("CX Dynamic Layout Configuration")

# Sidebar for user input
st.sidebar.header("Configure User")
selected_sheet = st.sidebar.selectbox("Select User Type, Fuel & Meter Type", list(data.keys()))
selected_attributes = st.sidebar.multiselect("Select User Attributes", user_attributes)

# --- Functions ---

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


def get_widget_order(df, attributes, applicable_widgets):
    """Determine widget order using attribute precedence and relative order."""
    widget_order = []
    widgets_without_order = len(applicable_widgets)

    for attr in attributes:
        if attr in df.columns and widgets_without_order > 0:
            attr_widgets = df[df['Widget Name'].isin(applicable_widgets)].sort_values(attr)
            for _, row in attr_widgets.iterrows():
                widget = row['Widget Name']
                if (
                    widget not in widget_order
                    and pd.notna(row[attr])
                    and row[attr] != 0
                ):
                    widget_order.append(widget)
                    widgets_without_order -= 1

    # Add any remaining widgets
    for widget in applicable_widgets:
        if widget not in widget_order:
            widget_order.append(widget)

    return widget_order


# --- Main App Logic ---

# Debugging: Show available sheets and ensure selected_sheet is valid
st.write("Available sheets:", list(data.keys()))

if selected_sheet in data:
    # Convert selected sheet data to DataFrame
    df = pd.DataFrame(data[selected_sheet])
    
    # Debugging: Print the column names to ensure the correct columns exist
    st.write("Available columns:", df.columns)

    # Rename columns if necessary (e.g., 'Widget/Page' to 'Widget Name')
    if 'Widget/Page' in df.columns:
        df = df.rename(columns={'Widget/Page': 'Widget Name'})

    # Ensure 'Widget Name' column exists
    if 'Widget Name' not in df.columns:
        st.error("The 'Widget Name' column is missing.")
    else:
        # Get applicable widgets based on selected attributes
        applicable_widgets = get_applicable_widgets(df, selected_attributes)

        # Get widget order
        widget_order = get_widget_order(df, selected_attributes, applicable_widgets)

        # Display widget order and images for each widget
        st.subheader(f"Widget Order for {selected_sheet}")
        
        for section in section_order:
            section_widgets = [
                w for w in widget_order if w in df[df['Section'] == section]['Widget Name'].values
            ]

            if section_widgets:
                st.write(f"**{section} Section:**")
                num_widgets = len(section_widgets)

                if num_widgets == 1:
                    widget_name = section_widgets[0]
                    widget_row = df[df['Widget Name'] == widget_name]
                    widget_image = widget_row['Image'].values[0]  # Get the image URL/path
                    
                    st.image(widget_image, caption=widget_name)
                else:
                    cols = st.columns(2)
                    for i, widget in enumerate(section_widgets):
                        widget_row = df[df['Widget Name'] == widget]
                        widget_image = widget_row['Image'].values[0]  # Get the image URL/path

                        with cols[i % 2]:
                            st.image(widget_image, caption=widget)
                st.write("")  # For spacing

        # Display raw data (optional)
        with st.expander("Show raw data"):
            st.dataframe(df)
else:
    st.error("Selected sheet not found in the data.")
