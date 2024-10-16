import streamlit as st
import pandas as pd
import json

# Load the JSON file
file_path = 'CX_Dynamic_Layouts_Config.json'  # Replace with the actual path to your JSON file
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

# Streamlit app
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

    # Add any remaining widgets (shouldn't happen based on the logic)
    for widget in applicable_widgets:
        if widget not in widget_order:
            widget_order.append(widget)

    return widget_order


# --- Main App Logic ---
if selected_sheet in data:
    # Load the sheet data as a DataFrame
    df = pd.DataFrame(data[selected_sheet])

    # Get applicable widgets
    applicable_widgets = get_applicable_widgets(df, selected_attributes)

    # Get widget order
    widget_order = get_widget_order(df, selected_attributes, applicable_widgets)

    # Display results with section ordering and layout
    st.subheader(f"Widget Order for {selected_sheet}")

    for section in section_order:
        section_widgets = [
            w for w in widget_order if w in df[df['Section'] == section]['Widget Name'].values
        ]

        if section_widgets:
            st.write(f"**{section} Section:**")
            num_widgets = len(section_widgets)

            if num_widgets == 1:
                st.write(f"- {section_widgets[0]} (Full Width)")
            else:
                cols = st.columns(2)
                for i, widget in enumerate(section_widgets):
                    with cols[i % 2]:
                        widget_display = widget
                        if i == num_widgets - 1 and num_widgets % 2 != 0:
                            widget_display += " (Full Width)"
                        st.write(f"- {widget_display}")
            st.write("")

    # Display raw data (optional)
    with st.expander("Show raw data"):
        st.dataframe(df)

else:
    st.error("Selected sheet not found in the JSON file.")
