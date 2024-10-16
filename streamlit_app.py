import streamlit as st
import pandas as pd
import json
from PIL import Image
import requests
from io import BytesIO

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
user_attributes = ['EV', 'TOU Rate', 'Solar', 'Budget Billing', 'Demand charge', 'Regular']

# Define section order
section_order = [
    "Last month",
    "Current month",
    "Insights & trends",
    "Promotions",
    "Carbon footprint",
]

# --- Functions ---

def get_applicable_widgets(df, attributes, kill_widgets=None):
    """Gets applicable widgets, handling 'KILL', 'PASS', and utility-killed widgets."""
    applicable_widgets = []
    for _, row in df.iterrows():
        widget = row['Widget Name']
        if widget is None or (kill_widgets and widget in kill_widgets):
            continue
        if 'Status (if applicable)' in df.columns and row['Status (if applicable)'] == 'OFF':
            continue

        if not attributes:  # If no attributes selected, show all widgets (except killed)
            applicable_widgets.append(widget)
            continue

        is_applicable = True
        for attr in attributes:
            if attr in df.columns and pd.notna(row.get(attr)):
                if row.get(attr) == "KILL":
                    is_applicable = False
                    break
                elif row.get(attr) == 'PASS' or row.get(attr) in [0, "", None]:
                    continue
                else:
                    is_applicable = True
                    break  # If any attribute is applicable, include the widget
        if is_applicable:
            applicable_widgets.append(widget)

    return [widget for widget in applicable_widgets if widget]  # Filter out None

def get_widget_order(df, attributes, applicable_widgets):
    """Determine widget order using attribute precedence and relative order."""
    widget_order = []
    widgets_without_order = applicable_widgets.copy()

    for attr in user_attributes:  # Iterate through user attributes in order of precedence
        if attr in attributes and attr in df.columns:
            # Sort only rows that have valid numeric values or comparable data for the attribute
            attr_widgets = df[df['Widget Name'].isin(widgets_without_order)]
            try:
                attr_widgets = attr_widgets[attr_widgets[attr].apply(lambda x: isinstance(x, (int, float)) or pd.notna(x))]
                attr_widgets = attr_widgets.sort_values(attr, ascending=False)
            except TypeError:
                continue  # Skip if the column contains incompatible types

            for _, row in attr_widgets.iterrows():
                widget = row['Widget Name']
                if pd.notna(row.get(attr)) and row.get(attr) not in ["KILL", "PASS", 0, "", None]:
                    widget_order.append(widget)
                    widgets_without_order.remove(widget)

    # Add any remaining widgets (that haven't been ordered by attributes)
    widget_order.extend(widgets_without_order)

    return widget_order

def display_widget_with_image(widget_name, image_path):
    try:
        if image_path.startswith('http'):
            response = requests.get(image_path)
            img = Image.open(BytesIO(response.content))
        else:
            img = Image.open(image_path)
        st.image(img, caption=widget_name, use_column_width=True)
    except Exception as e:
        st.write(f"{widget_name} (Image not available: {str(e)})")

# --- Main App Logic ---

st.title("CX Dynamic Layout Configuration")

# Sidebar for user input
st.sidebar.header("Configure User")
selected_sheet = st.sidebar.selectbox("Select User Type, Fuel & Meter Type", list(data.keys()))

if selected_sheet in data:
    df_initial = pd.DataFrame(data[selected_sheet])
    available_attributes = [attr for attr in user_attributes if attr in df_initial.columns]
    selected_attributes = st.sidebar.multiselect("Select User Attributes", available_attributes)
    kill_widgets = st.sidebar.multiselect("Widgets to Kill (Utility Level)", df_initial['Widget Name'].unique() if 'Widget Name' in df_initial else [])

    try:
        # Convert selected sheet data to DataFrame
        df = pd.DataFrame(data[selected_sheet])

        # Rename columns if necessary ('Widget/Page' to 'Widget Name')
        if 'Widget/Page' in df.columns:
            df = df.rename(columns={'Widget/Page': 'Widget Name'})

        # Get applicable widgets
        applicable_widgets = get_applicable_widgets(df, selected_attributes, kill_widgets)

        # Get widget order
        widget_order = get_widget_order(df, selected_attributes, applicable_widgets)

        # Display widget order and group by section
        st.subheader(f"Widget Order for {selected_sheet}")
        
        for section in section_order:
            section_widgets = [
                w for w in widget_order if w in df[df['Section'] == section]['Widget Name'].values
            ]

            if section_widgets:
                st.write(f"**{section} Section:**")
                for widget in section_widgets:
                    widget_row = df[df['Widget Name'] == widget]
                    if 'Image' in widget_row.columns and pd.notna(widget_row['Image'].values[0]):
                        image_path = widget_row['Image'].values[0]
                        display_widget_with_image(widget, image_path)
                    else:
                        st.write(f"- {widget}")
                st.write("")  # For spacing

        # Display raw data (optional)
        with st.expander("Show raw data"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.write("Debugging Information:")
        st.write(f"Selected Sheet: {selected_sheet}")
        st.write(f"Selected Attributes: {selected_attributes}")
        st.write(f"Applicable Widgets: {applicable_widgets if 'applicable_widgets' in locals() else 'Not calculated yet'}")
        if 'df' in locals():
            st.write(df.info())
            st.write(df.head())
else:
    st.error("Selected sheet not found in the data.")
