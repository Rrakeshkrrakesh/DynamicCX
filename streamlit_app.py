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

# Function to get applicable widgets
def get_applicable_widgets(df, attributes):
    applicable_widgets = []
    widget_column = 'Name of the widget or page within each section'
    status_column = 'Flag to signify whether the widget is "New or Existing"'
    
    for _, row in df.iterrows():
        if widget_column not in row or status_column not in row:
            st.error(f"Required columns not found in the sheet. Expected '{widget_column}' and '{status_column}'")
            return []
        
        widget = row[widget_column]
        is_applicable = False
        for attr in attributes:
            if attr in df.columns and pd.notna(row[attr]) and row[attr] != 0:
                is_applicable = True
                break
        if is_applicable and row[status_column] != 'OFF':
            applicable_widgets.append(widget)
    return applicable_widgets

# Function to get widget order
def get_widget_order(df, attributes, applicable_widgets):
    widget_order = []
    widget_column = 'Name of the widget or page within each section'
    
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
    
    # Display raw data
    with st.expander("Show raw data"):
        st.dataframe(df)
    
    # Get applicable widgets
    applicable_widgets = get_applicable_widgets(df, selected_attributes)
    
    if applicable_widgets:
        # Get widget order
        widget_order = get_widget_order(df, selected_attributes, applicable_widgets)
        
        # Display results
        st.subheader(f"Widget Order for {selected_sheet}")
        section_column = 'Section name is assigned to a group of similar widgets'
        if section_column in df.columns:
            for section in df[section_column].unique():
                st.write(f"**{section} Section:**")
                section_widgets = [w for w in widget_order if w in df[df[section_column] == section]['Name of the widget or page within each section'].values]
                for i, widget in enumerate(section_widgets):
                    st.write(f"{i+1}. {widget}")
                st.write("")
        else:
            st.error(f"Section column '{section_column}' not found in the sheet.")
    else:
        st.warning("No applicable widgets found for the selected attributes.")

else:
    st.error("Selected sheet not found in the Excel file.")

# Explanation of the logic
st.markdown("""
### How it works:
1. User selects the sheet (User Type, Fuel & Meter Type) and user attributes.
2. The system identifies applicable widgets based on the selected attributes and whether they're turned on.
3. Widgets are ordered based on the precedence of user attributes (EV > TOU > Solar > Budget Billing > Demand Charge).
4. Widgets are grouped by sections, maintaining their relative order within each section.
5. The final order of widgets is displayed for each section.
""")
