import streamlit as st
import pandas as pd

# Load the Excel file
@st.cache_data
def load_excel(file_path):
    return pd.ExcelFile(file_path)

file_path = 'CX_Dynamic_Layouts_Config.xlsx'
xls = load_excel(file_path)

# Streamlit app
st.set_page_config(page_title="CX Dynamic Layout Configuration", layout="wide")
st.title("CX Dynamic Layout Configuration")

# Sheet selection
sheet_names = xls.sheet_names
selected_sheet = st.selectbox("Select Sheet", sheet_names)

# Load selected sheet
@st.cache_data
def load_sheet_data(xls, sheet_name):
    return pd.read_excel(xls, sheet_name=sheet_name)

df = load_sheet_data(xls, selected_sheet)

# Display sheet info
st.subheader("Sheet Information")
st.write(f"Number of rows: {df.shape[0]}")
st.write(f"Number of columns: {df.shape[1]}")

# Display column names and types
st.subheader("Column Names and Types")
col_info = pd.DataFrame({
    "Column Name": df.columns,
    "Data Type": df.dtypes,
    "Non-Null Count": df.notna().sum(),
    "Unique Values": [df[col].nunique() for col in df.columns]
})
st.dataframe(col_info)

# Manual column selection
st.subheader("Select Relevant Columns")
widget_column = st.selectbox("Select Widget Column", [""] + list(df.columns))
status_column = st.selectbox("Select Status Column (optional)", [""] + list(df.columns))
section_column = st.selectbox("Select Section Column (optional)", [""] + list(df.columns))

# Display sample data
st.subheader("Sample Data (First 5 Rows)")
st.dataframe(df.head())

# Process data if columns are selected
if widget_column:
    st.subheader("Widgets")
    widgets = df[widget_column].dropna().unique()
    st.write(f"Number of unique widgets: {len(widgets)}")
    st.write("Unique widget names:")
    st.write(widgets)

    if status_column:
        st.subheader("Widget Status")
        status_counts = df[status_column].value_counts()
        st.write(status_counts)

    if section_column:
        st.subheader("Sections")
        sections = df[section_column].dropna().unique()
        st.write(f"Number of unique sections: {len(sections)}")
        st.write("Unique section names:")
        st.write(sections)

    # User attributes selection
    st.subheader("Select User Attributes")
    user_attributes = st.multiselect("User Attributes", [col for col in df.columns if col not in [widget_column, status_column, section_column]])

    if user_attributes:
        st.subheader("Widget Order")
        ordered_widgets = []
        for attr in user_attributes:
            attr_widgets = df.sort_values(attr)[widget_column].dropna().unique()
            ordered_widgets.extend([w for w in attr_widgets if w not in ordered_widgets])

        if section_column:
            for section in df[section_column].dropna().unique():
                st.write(f"**{section}**")
                section_widgets = [w for w in ordered_widgets if w in df[df[section_column] == section][widget_column].values]
                for i, widget in enumerate(section_widgets, 1):
                    st.write(f"{i}. {widget}")
                st.write()
        else:
            for i, widget in enumerate(ordered_widgets, 1):
                st.write(f"{i}. {widget}")

else:
    st.warning("Please select a Widget Column to proceed.")

# Explanation
st.markdown("""
### How to use this tool:
1. Select the appropriate sheet from the dropdown.
2. Review the sheet information and column details.
3. Select the relevant columns for Widget, Status (optional), and Section (optional).
4. Review the sample data to confirm your column selections.
5. If a Widget Column is selected, you'll see unique widget names and can select user attributes.
6. The tool will display the widget order based on your selections.

This interactive approach allows you to explore the data and manually select the relevant columns, 
providing more flexibility in handling different Excel file structures.
""")
