import streamlit as st
import pandas as pd

# Load the Excel file
file_path = 'CX_Dynamic_Layouts_Config.xlsx'  # Replace with your actual file path
xls = pd.ExcelFile(file_path)

# Load all sheets
sheet_names = xls.sheet_names
data = {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in sheet_names}

# Define user attributes and their order of precedence
user_attributes = ['EV', 'TOU', 'Solar', 'Budget Billing', 'Demand Charge', 'Regular']

# Streamlit app
st.set_page_config(page_title="CX Dynamic Layout Configuration", layout="wide")
st.title("CX Dynamic Layout Configuration")

# Sidebar for user input
st.sidebar.header("Configure User")
selected_sheet = st.sidebar.selectbox("Select User Type, Fuel & Meter Type", sheet_names)
selected_attributes = st.sidebar.multiselect("Select User Attributes", user_attributes)

# Function to get applicable widgets
def get_applicable_widgets(df, attributes):
    if not attributes:  # Handle case with no selected attributes
        return df[df['Status'] != 'OFF']['Widget Name'].tolist()

    applicable_widgets = []
    for _, row in df.iterrows():
        widget = row['Widget Name']
        if row['Status'] == 'OFF':
            continue
        is_applicable = any(
            attr in df.columns and pd.notna(row[attr]) and row[attr] != 0 for attr in attributes
        )
        if is_applicable:
            applicable_widgets.append(widget)
    return applicable_widgets

# Function to get widget order
def get_widget_order(df, attributes, applicable_widgets):
    widget_order = []
    for attr in attributes:
        if attr in df.columns:
            # (You can add logic here for within-attribute ordering if needed)
            attr_widgets = df[df['Widget Name'].isin(applicable_widgets)].sort_values(attr)
            for widget in attr_widgets['Widget Name']:
                if widget not in widget_order and pd.notna(
                    df.loc[df['Widget Name'] == widget, attr].iloc[0]
                ):
                    widget_order.append(widget)

    # Add any remaining widgets
    for widget in applicable_widgets:
        if widget not in widget_order:
            widget_order.append(widget)

    return widget_order

# Main app logic
if selected_sheet in data:
    df = data[selected_sheet]

    # Get applicable widgets
    applicable_widgets = get_applicable_widgets(df, selected_attributes)

    # Get widget order
    widget_order = get_widget_order(df, selected_attributes, applicable_widgets)

    # Display results (using st.columns for multi-column layout)
    st.subheader(f"Widget Order for {selected_sheet}")
    for section in df['Section'].unique():
        st.write(f"**{section} Section:**")
        section_widgets = [
            w for w in widget_order if w in df[df['Section'] == section]['Widget Name'].values
        ]

        # Create columns (adjust the number of columns as needed)
        cols = st.columns(3) 
        for i, widget in enumerate(section_widgets):
            with cols[i % 3]:  # Distribute widgets across columns
                st.write(f"- {widget}")
        st.write("")  # Add spacing between sections

    # Display raw data (optional)
    with st.expander("Show raw data"):
        st.dataframe(df)

else:
    st.error("Selected sheet not found in the Excel file.")

# Explanation of the logic (optional)
st.markdown(
    """
### How it works:
1. **User selects the sheet (User Type, Fuel & Meter Type) and user attributes.**
2. **The system identifies applicable widgets based on:**
   - Selected user attributes.
   - Whether the widget's "Status" is set to "ON" in the Excel data. 
3. **Widgets are ordered based on the precedence of user attributes:** 
   - EV > TOU > Solar > Budget Billing > Demand Charge > Regular
4. **Widgets are grouped by sections, maintaining their relative order within each section.**
5. **The final order of widgets is displayed for each section.** 
"""
)
