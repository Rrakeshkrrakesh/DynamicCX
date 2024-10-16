import streamlit as st
import pandas as pd
import json

# Load the JSON file
with open('CX_Dynamic_Layouts_Config.json') as f:
    data = json.load(f)

# Convert to DataFrame for the selected sheet
selected_sheet = "Sheet1"  # Example, replace with user selection
df = pd.DataFrame(data[selected_sheet])

# Clean up the DataFrame by dropping unwanted columns and rows with null values
df = df.drop(columns=[col for col in df.columns if "Unnamed" in col or df[col].isnull().all()])

# Rename columns if needed (e.g., 'Widget/Page' to 'Widget Name')
df = df.rename(columns={'Widget/Page': 'Widget Name'})

# Ensure critical columns are not null (add default values if necessary)
df['Widget Name'] = df['Widget Name'].fillna('Unknown Widget')
df['Section'] = df['Section'].fillna('Misc')

# Now, proceed with the rest of your logic
# Define user attributes and their order of precedence
user_attributes = ['EV', 'TOU Rate', 'Solar', 'Budget Billing', 'Demand charge', 'Regular']

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
st.set_page_config(page_title="CX Dynamic Layout Configuration", layout="wide")
st.title("CX Dynamic Layout Configuration")

# Sidebar for user input
selected_attributes = st.sidebar.multiselect("Select User Attributes", user_attributes)

# Get applicable widgets
applicable_widgets = get_applicable_widgets(df, selected_attributes)

# Get widget order
widget_order = get_widget_order(df, selected_attributes, applicable_widgets)

# Display results with section ordering and layout
st.subheader(f"Widget Order for {selected_sheet}")

section_order = ["Last month", "Current month", "Insights & trends", "Promotions", "Carbon Footprint"]
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
