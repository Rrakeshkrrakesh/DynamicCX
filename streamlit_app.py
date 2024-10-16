import streamlit as st
import pandas as pd
import json

# Streamlit app configuration (must be the first Streamlit command)
st.set_page_config(page_title="CX Dynamic Layout Configuration", layout="wide")

# Load the JSON data
file_path = 'CX_Dynamic_Layouts_Config.json'  # Replace with your actual JSON file path
try:
    with open(file_path) as f:
        data = json.load(f)
    st.sidebar.success(f"Successfully loaded data from {file_path}")
except FileNotFoundError:
    st.error(f"Error: File '{file_path}' not found. Please check the file path.")
    st.stop()
except json.JSONDecodeError:
    st.error(f"Error: Unable to parse '{file_path}'. Please ensure it's a valid JSON file.")
    st.stop()

# Define user attributes and their order of precedence
user_attributes = ['EV', 'TOU Rate', 'Solar', 'Budget Billing', 'Demand charge', 'Regular'] # Corrected attribute names

# Define section order
section_order = [
    "Last month",
    "Current month",
    "Insights & trends",
    "Promotions",
    "Carbon footprint",  # Or Carbon Footprint (check your data for consistency)
]


# --- Functions ---

def get_applicable_widgets(df, attributes, kill_widgets=None):
    """Gets applicable widgets, handling 'KILL', 'PASS', and utility-killed widgets."""
    applicable_widgets = []
    for _, row in df.iterrows():
        widget = row['Widget Name']
        if 'Status (if applicable)' in df.columns and row['Status (if applicable)'] == 'OFF':
            continue
        if kill_widgets and widget in kill_widgets:
            continue

        if not attributes:  # If no attributes selected, show all widgets (except killed)
            applicable_widgets.append(widget)
            continue

        is_applicable = False
        for attr in attributes:
            if attr in df.columns and pd.notna(row.get(attr)):
                if row.get(attr) == "KILL" or row.get(attr) == 0:
                    is_applicable = False
                    break  # Important: Exit the inner loop if KILL is encountered
                elif row.get(attr) != 'PASS' and row.get(attr) != 0 and row.get(attr) != "":
                    is_applicable = True
        if is_applicable:
            applicable_widgets.append(widget)

    return applicable_widgets



def get_widget_order(df, attributes, applicable_widgets):
    """Determine widget order using attribute precedence and relative order."""
    widget_order = []
    widgets_without_order = len(applicable_widgets)

    for attr in user_attributes: # Iterate through user attributes in order of precedence
        if attr in attributes and attr in df.columns and widgets_without_order > 0:
            attr_widgets = df[df['Widget Name'].isin(applicable_widgets)].sort_values(attr)
            for _, row in attr_widgets.iterrows():
                widget = row['Widget Name']
                if widget not in widget_order and pd.notna(row.get(attr)) and row.get(attr) != 0:
                    widget_order.append(widget)
                    widgets_without_order -= 1

    # Add any remaining widgets (that haven't been ordered by attributes)
    for widget in applicable_widgets:
        if widget not in widget_order:
            widget_order.append(widget)

    return widget_order



# --- Main App Logic ---

st.title("CX Dynamic Layout Configuration")

# Sidebar for user input
st.sidebar.header("Configure User")
selected_sheet = st.sidebar.selectbox("Select User Type, Fuel & Meter Type", list(data.keys()))
if selected_sheet in data:  # Check if the sheet exists before accessing it
    df_initial = pd.DataFrame(data[selected_sheet])
    selected_attributes = st.sidebar.multiselect("Select User Attributes", [attr for attr in user_attributes if attr in df_initial.columns])
    # Utility-level widget kill configuration
    kill_widgets = st.sidebar.multiselect("Widgets to Kill (Utility Level)", df_initial['Widget Name'].unique() if 'Widget Name' in df_initial else [])
else:
    st.error("Selected sheet not found in the data.")
    st.stop()  # Stop execution if the sheet isn't found

if selected_sheet in data:
    try:
        # Convert selected sheet data to DataFrame
        df = pd.DataFrame(data[selected_sheet])


        # Rename columns if necessary ('Widget/Page' to 'Widget Name')
        if 'Widget/Page' in df.columns:
            df = df.rename(columns={'Widget/Page': 'Widget Name'})
        # ... (rest of the data processing and display logic as before)


    except Exception as e:
        # ... (enhanced error handling and debugging as before)
