import streamlit as st
import pandas as pd

# Load the Excel file
file_path = 'CX_Dynamic_Layouts_Config.xlsx'
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

# Function to get column names
def get_column_names(df):
    widget_column = None
    status_column = None
    section_column = None

    for col in df.columns:
        if 'widget' in col.lower() or 'name' in col.lower():
            widget_column = col
        elif 'status' in col.lower() or 'flag' in col.lower():
            status_column = col
        elif 'section' in col.lower():
            section_column = col
    
    return widget_column, status_column, section_column

# Function to get applicable widgets
def get_applicable_widgets(df, attributes, widget_column, status_column):
    applicable_widgets = []
    
    for _, row in df.iterrows():
        widget = row[widget_column]
        is_applicable = False
        for attr in attributes:
            if attr in df.columns and pd.notna(row[attr]) and row[attr] != 0:
                is_applicable = True
                break
        if is_applicable and (status_column is None or row[status_column] != 'OFF'):
            applicable_widgets.append(widget)
    return applicable_widgets

# Function to get widget order
def get_widget_order(df, attributes, applicable_widgets, widget_column):
    widget_order = []
    
    for attr in attributes:
        if attr in df.columns:
            attr_widgets = df[df[widget_column].isin(applicable_widgets)].sort_values(attr)
            for widget in attr_widgets[widget_column]:
                if widget not in widget_order and pd.notna(df.loc[df[widget_column] == widget, attr].iloc[0]):
                    widget_order.append(widget)
    
    # Add any remaining widgets
    for widget in applicable_widgets:
        if widget not in widget_order:
            widget_order.append(widget)
    
    return widget_order

# Main app logic
if selected_sheet in data:
    df = data[selected_sheet]
    
    # Display column names
    st.subheader("Column Names in the Sheet")
    st.write(df.columns.tolist())
    
    # Display raw data
    with st.expander("Show raw data (first 5 rows)"):
        st.dataframe(df.head())
    
    # Get column names
    widget_column, status_column, section_column = get_column_names(df)
    
    if widget_column:
        st.success(f"Widget column found: '{widget_column}'")
    else:
        st.error("Widget column not found. Please check the column names.")
    
    if status_column:
        st.success(f"Status column found: '{status_column}'")
    else:
        st.warning("Status column not found. The app will proceed without checking widget status.")
    
    if section_column:
        st.success(f"Section column found: '{section_column}'")
    else:
        st.warning("Section column not found. Widgets will not be grouped by section.")
    
    # Get applicable widgets
    if widget_column:
        applicable_widgets = get_applicable_widgets(df, selected_attributes, widget_column, status_column)
        
        if applicable_widgets:
            # Get widget order
            widget_order = get_widget_order(df, selected_attributes, applicable_widgets, widget_column)
            
            # Display results
            st.subheader(f"Widget Order for {selected_sheet}")
            if section_column:
                for section in df[section_column].unique():
                    st.write(f"**{section} Section:**")
                    section_widgets = [w for w in widget_order if w in df[df[section_column] == section][widget_column].values]
                    for i, widget in enumerate(section_widgets):
                        st.write(f"{i+1}. {widget}")
                    st.write("")
            else:
                for i, widget in enumerate(widget_order):
                    st.write(f"{i+1}. {widget}")
        else:
            st.warning("No applicable widgets found for the selected attributes.")
    else:
        st.error("Cannot process widgets without a valid widget column.")

else:
    st.error("Selected sheet not found in the Excel file.")

# Explanation of the logic
st.markdown("""
### How it works:
1. User selects the sheet (User Type, Fuel & Meter Type) and user attributes.
2. The system attempts to identify the correct columns for widgets, status, and sections.
3. Applicable widgets are determined based on the selected attributes and status (if available).
4. Widgets are ordered based on the precedence of user attributes.
5. If a section column is found, widgets are grouped by sections, maintaining their relative order within each section.
6. The final order of widgets is displayed, either by section or as a single list.
""")
