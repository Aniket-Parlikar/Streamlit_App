# Assessment for Ateios Systems

# Import all the necessary modules
import pandas as pd
import streamlit as st

# Define the download button key
download_button_key = "download_button_key"

# Function to plot a Linechart
@st.cache_data
def plot_linechart(data):
    '''
    Plot a Line Chart based on Input data
    '''
    st.header("Graph of plot Voltage over time")
    st.write('Voltage vs Time for Cell ID 230928-4')
    st.line_chart(data, x='Real_Time', y='Voltage')

# Define a function to read and preprocess data
@st.cache_data
def read_data(upload_file, name):
    '''
    Read and preprocess the input data
    '''
    if name.endswith("xlsx"):
        data = pd.read_excel(upload_file)
    
    if name.endswith("csv"):
        data = pd.read_csv(upload_file)

    if list(data.columns)!=list(ncol_dict.keys()):
        data = pd.DataFrame()
    else:
        data = data.rename(columns=ncol_dict)
        data['Specific_Capacity'] = (data['Capacity'] / data['Cathode_Active_Material_Mass'])*1000
        data['Real_Time']=pd.to_datetime(data['Real_Time'])
    return data

# Define a function to query required cell data
@st.cache_data
def get_celldata(data):
    '''
    Query and return the required cell data
    '''
    return data[data['Cell_ID'] == '230928-4']

# Define a function to get the pivot data
@st.cache_data
def get_pivot_data(data):
    '''
    Get the Pivot Tables and Aggregate Tables
    '''
    filtered_pivot = data[data['Step_Type'] == 'CC_DChg']
    pivot_df = filtered_pivot.pivot_table(values='Specific_Capacity', index='Cycle_ID', columns='Cell_ID', aggfunc='max')
    agg_df = pivot_df.agg(['mean','std'],axis=1)
    return pivot_df, agg_df

# Define a function to convert to CSV
@st.cache_data
def convert_df(df):
    '''
    Convert the dataframe to csv
    '''
    # df.reset_index(inplace=True, drop=True)
    return df.to_csv(index=False).encode('utf-8')

# Callback function after downloading data
@st.cache_data
def callback(data):
    st.session_state['data'] = data
    st.session_state['is_uploaded'] = 1

# Define a function to hide the file uploader
# @st.cache_data
# def hide_uploader(upload_flag):
#     '''
#     Hide the file uploader from the user
#     '''
#     if upload_flag==1:
#         # Inject custom HTML and CSS to hide the file uploader widget 
#         st.markdown(
#             """
#             <style>
#                 #please-upload-your-csv-file{
#                     display: none;
#                 }
#                 div[data-testid="stFileUploader"] {
#                     display: none;
#                 }
#             </style>
#             """,
#             unsafe_allow_html=True
#         )

## Rename the columns
ncol_dict = {'Current (mA)':'Current', 'Capacity (mAh)':'Capacity', 'Energy (mWh)':'Energy',
       'Record Serial Number':'Record_Serial_Number', 'Cycle ID':'Cycle_ID', 'Step ID':'Step_ID', 'Real Time':'Real_Time', 'Step Type':'Step_Type',
       'Step Time':'Step_Time', 'Voltage (V)':'Voltage', 'Power (W)':'Power', 'Cell ID':'Cell_ID',
       'Cathode Active Material Mass (mg)':'Cathode_Active_Material_Mass'}

## Create a data uploader object
st.title('Homepage')
col1, col2 = st.columns([0.8, 0.2])


# Initialize the session state paramenters
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame()

if 'is_uploaded' not in st.session_state:
    st.session_state.is_uploaded = 0

if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Check if
    # st.header('Please upload your excel file.')
filename = st.file_uploader("Please select a file to upload",help="Enter a file to be uploaded",type=['xlsx','csv'])

if filename:
    st.session_state['uploaded_file'] = filename.name
    # st.write(filename.name)

# Check if the file has been uploaded
if filename is not None or st.session_state['is_uploaded']==1:

    # If the filename is None
    if filename:
        #st.session_state["uploaded_file"] = filename.name
        name = filename.name
        data1 = read_data(filename,name)
        st.session_state['data'] = data1
    else:
        data1 = pd.DataFrame()
    # data1 = st.session_state['data']

    # If the dataframe is empty
    if data1.isna().all().all():
        st.error('You have entered an incorrect or blank file. Please re-upload.')
        st.session_state['is_uploaded'] = 0
    else:
        st.session_state['is_uploaded'] = 1

        # Hide the uploader once used
        # hide_uploader(st.session_state['is_uploaded'])

         # download_ui(data1)
        # st.write(st.session_state["uploaded_file"])
        csv = convert_df(data1)

        # Create the download button


        # Get the aggregated data
        cell_data = get_celldata(data1)
        pivot_df, agg_df= get_pivot_data(data1)

        st.write("Finished reading the data. You can continue")

        with col2:
            st.download_button(
            label="Download",
            data=csv,
            file_name='output.csv',
            mime='text/csv',
            key = download_button_key,
            on_click=callback(data1)
            )
    
        # Define the necessary tabs and their functionalaties
        tab1, tab2,tab3 = st.tabs(["Graphs","Pivot Table","Aggregate Table"])

        # Plot a Line Chart on the tab1
        with tab1:
            plot_linechart(cell_data)
        
        # Display the Pivot Table on the tab2
        with tab2:
            st.title("Maximum Specific Capacity Table")
            st.write('The given table displays the maximum Specific Capacity value for every Cycle ID only for Step type "CC_DChg".')
            st.table(pivot_df)

        # Display the Aggregates Table on tab3
        with tab3:
            st.title('''Mean and std deviation table''')            
            st.write(" The table shows the mean and standard deviation of Max Specific Capacity values for every Cycle ID(1 to 5).")
            st.table(agg_df)
