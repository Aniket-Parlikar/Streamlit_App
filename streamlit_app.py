# Assessment for Ateios Systems

'''
Workflow of the app:
1) Have a horizontal/vertical navbar
2) On each page have the respective functionalities
    - On Page 1, Plot the graph for the mentioned data
    - On Page 2, Display the table for the data as according to Step 3
    - On Page 3, Display the table for the data as mentioned according to Step 4

    
3)TODO 
# Validate data that is entered into the GUI. It should be of excel and csv format and should have the necessary data format.
'''

# Import all the necessary modules
import pandas as pd
import streamlit as st

# Define the download button key
download_button_key = "download_button_key"

@st.cache_data
def preprocess_data(data):
    # Query the plotted data
    # df = st.session_state['data']
    cell_df = data[data['Cell_ID']=='230928-4']
    
    data['Specific_Capacity'] = (data['Capacity']/data['Cathode_Active_Material_Mass']) * 1000

    # Filter the data for Step Type 'CC_DChg'
    filtered_pivot = data[data['Step_Type'] == 'CC_DChg']

    return filtered_pivot

@st.cache_data
def plot_linechart(data):
    st.header("Graph of plot Voltage over time")
    st.write('Voltage vs Time for Cell ID 230928-4')
    st.line_chart(data, x='Real_Time', y='Voltage')

# Define a function to read and preprocess data
@st.cache_data
def read_data(upload_file):
    # Read the uploaded file
    data = pd.read_excel(upload_file)

    if list(data.columns)!=list(ncol_dict.keys()):
        # st.error('You have entered the incorrect file')
        data = pd.DataFrame()
    else:
        # Rename columns
        data = data.rename(columns=ncol_dict)
        data['Specific_Capacity'] = (data['Capacity'] / data['Cathode_Active_Material_Mass'])*1000
        data['Real_Time']=pd.to_datetime(data['Real_Time'])
        # data.set_index('Real_Time',inplace=True)
    return data

@st.cache_data
def get_celldata(data):
    return data[data['Cell_ID'] == '230928-4']

@st.cache_data
def get_pivot_data(data):
    filtered_pivot = data[data['Step_Type'] == 'CC_DChg']
    pivot_df = filtered_pivot.pivot_table(values='Specific_Capacity', index='Cycle_ID', columns='Cell_ID', aggfunc='max')
    agg_df = pivot_df.agg(['mean','std'],axis=1)
    return pivot_df, agg_df

@st.cache_data
def convert_df(df):
    # df.reset_index(inplace=True, drop=True)
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data
def callback(data):
    st.session_state['data'] = data
    st.session_state['is_uploaded'] = 1

@st.cache_data
def hide_uploader(upload_flag):
    if upload_flag==1:
        # Inject custom HTML and CSS to hide the file uploader widget 
        st.markdown(
            """
            <style>
                #please-upload-your-csv-file{
                    display: none;
                }
                div[data-testid="stFileUploader"] {
                    display: none;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

## Rename the columns
ncol_dict = {'Current (mA)':'Current', 'Capacity (mAh)':'Capacity', 'Energy (mWh)':'Energy',
       'Record Serial Number':'Record_Serial_Number', 'Cycle ID':'Cycle_ID', 'Step ID':'Step_ID', 'Real Time':'Real_Time', 'Step Type':'Step_Type',
       'Step Time':'Step_Time', 'Voltage (V)':'Voltage', 'Power (W)':'Power', 'Cell ID':'Cell_ID',
       'Cathode Active Material Mass (mg)':'Cathode_Active_Material_Mass'}

## Create a data uploader object
st.title('Homepage')
col1, col2 = st.columns([0.8, 0.2])

if 'data' not in st.session_state:
    st.session_state['data'] = None

if 'is_uploaded' not in st.session_state:
    st.session_state.is_uploaded = 0

if 'uploaded_file' not in st.session_state or st.session_state.is_uploaded!=1:
    st.header('Please upload your csv file')
    filename = st.file_uploader("Please select a file to upload",help="Enter a file to be uploaded",key="uploaded_file",type=['xlsx'])
    #st.session_state.uploaded_file = filename
else:
    filename = st.session_state.uploaded_file

if filename is not None or st.session_state['is_uploaded']==1:

    if filename:
        data1 = read_data(filename)
        st.session_state['data'] = data1
    else:
        data1 = st.session_state['data']

    if data1.isna().all().all():
        st.error('You have entered incorrect file. Please enter a different file.')
        st.session_state['is_uploaded'] = 0
    else:
        st.session_state['is_uploaded'] = 1

         # Hide the uploader once used
        hide_uploader(st.session_state['is_uploaded'])

         # download_ui(data1)
        csv = convert_df(data1)

        # Create the download button

        with col2:
            st.download_button(
            label="Download",
            data=csv,
            file_name='output.csv',
            mime='text/csv',
            key = download_button_key,
            on_click=callback(data1)
            )

        # Get the aggregated data
        cell_data = get_celldata(data1)
        pivot_df, agg_df= get_pivot_data(data1)

        st.write("Finished reading the data. You can continue")
    
        # Define the necessary tabs and their functionalaties
        # create_tabs(data1)

        tab1, tab2,tab3 = st.tabs(["Graphs","Pivot Table","Aggregate Table"])

        with tab1:
            plot_linechart(cell_data)
        
        with tab2:
            st.title("Maximum Specific Capacity Table")
            st.write('The given table displays the maximum Specific Capacity value for every Cycle ID only for Step type "CC_DChg".')
            st.table(pivot_df)
        
        with tab3:
            st.title('''Mean and std deviation table''')            
            st.write(" The table shows the mean and standard deviation of Max Specific Capacity values for every Cycle ID(1 to 5).")
            st.table(agg_df)
