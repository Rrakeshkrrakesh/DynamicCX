import streamlit as st
import pandas as pd
import json
from PIL import Image
import requests
from io import BytesIO

# Streamlit app configuration
st.set_page_config(page_title="CX Dynamic Layout Configuration", layout="wide")

# Load JSON data
file_path = 'CX_Dynamic_Layouts_Config.json'
try:
    with open(file_path) as f:
        data = json.load(f)
    st.sidebar.success(f"Successfully loaded data from {file_path}")
except (FileNotFoundError, json.JSONDecodeError) as e:
    st.error(f"Error loading JSON: {e}")
    st.stop()

# User attributes and section order (as before)
user_attributes = ['EV', 'TOU Rate', 'Solar', 'Budget Billing', 'Demand charge', 'Regular']
section_order = ["Last month", "Current month", "Insights & trends", "Promotions", "Carbon footprint"]

# --- Functions ---
def get_applicable_widgets(df, attributes, kill_widgets=None):
    applicable_widgets = []
    for _, row in df.iterrows():
        widget = row['Widget Name']
        if 'Status (if applicable)' in df.columns and row['Status (if applicable)'] == 'OFF':
            continue
        if kill_widgets and widget in kill_widgets:
            continue

        if not attributes:
            applicable_widgets.append(widget)
            continue

        is_applicable = False # Correct initial value
        for attr in attributes:
            if attr in df.columns and pd.notna(row.get(attr)):
                if row.get(attr) == "KILL" or row.get(attr) == 0:
                    is_applicable = False
                    break
                elif row.get(attr) != 'PASS' and row.get(attr) != '' and pd.notna(row[attr]):
                    is_applicable = True
                    break
        if is_applicable:  # Only append if is_applicable is True
           applicable_widgets.append(widget)

    return applicable_widgets

def get_widget_order(df, attributes, applicable_widgets):
    widget_order = []
    widgets_without_order = applicable_widgets.copy()

    for attr in user_attributes:
        if attr in attributes and attr in df.columns:
            attr_widgets = df[df['Widget Name'].isin(widgets_without_order)].sort_values(attr)
            for _, row in attr_widgets.iterrows():
                widget = row['Widget Name']
                if pd.notna(row.get(attr)) and row.get(attr) not in ["KILL", "PASS", "", "0"]: # Check for non-zero and non-empty order
                    if isinstance(row[attr], (int, float)) and row[attr] > 0 : # Numerical order must be > 0
                        widget_order.append(widget)
                        widgets_without_order.remove(widget)

    widget_order.extend(widgets_without_order)
    return widget_order

def display_widget_with_image(widget_name, image_path):
    try:
        if image_path.startswith('http'):  # Handle URLs
            response = requests.get(image_path, stream=True) # Stream for large files
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            img = Image.open(BytesIO(response.content))
        else: # Handle Local files
            img = Image.open(image_path)
        st.image(img, caption=widget_name, use_column_width=True)
    except Exception as e:
        st.write(f"{widget_name} (Image not available: {e})")


# --- Main App Logic ---

st.title("CX Dynamic Layout Configuration")

# Sidebar
st.sidebar.header("Configure User")
selected_sheet = st.sidebar.selectbox("Select User Type...", list(data.keys()))


if selected_sheet in data and data[selected_sheet]:  # Check for data
    df_initial = pd.DataFrame(data[selected_sheet])
    # ... (rest of the sidebar setup)

    try:
        df = pd.DataFrame(data[selected_sheet])

        # Rename the Widget column FIRST
        if 'Widget/Page' in df.columns:
            df = df.rename(columns={'Widget/Page': 'Widget Name'})
        
        widget_name_column = 'Widget Name' if 'Widget Name' in df.columns else 'Widget/Page'


        # ... (get_applicable_widgets, get_widget_order calls)

        # Display
        st.subheader(f"Widget Order for {selected_sheet}")
        for section in section_order:
            section_widgets = [w for w in widget_order if w in df[df['Section'] == section][widget_name_column].values]
            if section_widgets:
                st.write(f"**{section} Section:**")
                for widget in section_widgets:
                    widget_row = df[df[widget_name_column] == widget].iloc[0]  # .iloc[0] to get the first row
                    if 'Image' in df.columns and pd.notna(widget_row['Image']):
                        image_path = widget_row['Image']

                        display_widget_with_image(widget, image_path)

                    else:
                        st.write(f"- {widget}")
                st.write("")  # Spacing

        # ... (Raw data expander)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        # ... (debugging info)

else:
    st.error("Selected sheet not found or empty.")
