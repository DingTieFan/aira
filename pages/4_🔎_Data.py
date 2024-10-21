import streamlit as st
import pandas as pd
from utils.data_helper import dws_etl, list_files, delete_file
import os 
from pathlib import Path

storage_path = st.session_state.get('storage_path')
performance_table_name = 'performance_table.csv'
loan_table_name = 'loan_table.csv'
repayment_table_name = 'repayment_table.csv'
application_table_name = 'application_table.csv'

@st.cache_data  # 👈 添加缓存装饰器
def load_data(url):
    df = pd.read_csv(url)
    return df

page = st.sidebar.radio("Navigation", ["Data Loader", "Data Manager"])

if page == "Data Loader":
    # File uploader section
    st.header("Data Source")
    st.write(st.session_state)

    # Upload files
    app_file = st.file_uploader("Application Table", type=["csv"])
    loan_file = st.file_uploader("Loan Table", type=["csv"])
    repayment_file = st.file_uploader("Repayment Table", type=["csv"])

    label_mapping = {
        "Application Table": application_table_name,
        "Loan Table": loan_table_name,
        "Repayment Table": repayment_table_name
    }
    # Function to display file info, with delete and download on the same row
    def display_file(file, label):
        
        if file is not None:
            df = pd.read_csv(file)
            # Save the file to the data directory
            file_path = '{}/{}'.format(storage_path, file.name)

            df.to_csv(file_path, index=False)
            st.session_state[label_mapping.get(label)] = '{}/{}'.format(storage_path, file.name)
   
    # Display each file section
    display_file(app_file, "Application Table")
    display_file(loan_file, "Loan Table")
    display_file(repayment_file, "Repayment Table")


    # Data preparation section
    st.header("Data Preparation")

    delinquency = st.selectbox("Delinquency:", ['only principal', 'principal + interest'])
    chargeoff_cutoff = st.selectbox("Chargeoff cutoff:", ['-', '180', '150', '120', '90', '60'])

    
    if st.button("Process Files"):
        try:
           
            loan_table_df = load_data(st.session_state[loan_table_name])
            repayment_table_df = load_data(st.session_state[repayment_table_name])

            dws_df = dws_etl(loan_table_df, repayment_table_df, delinquency, chargeoff_cutoff)
            dws_df.to_csv('{}/{}'.format(storage_path, performance_table_name), index=False)
            st.session_state[performance_table_name] = '{}/{}'.format(storage_path, performance_table_name)
            st.write("performance_table save to {}".format(storage_path))
        except Exception as e:
            st.error(f"An error occurred: {e}")


if page == "Data Manager":
    st.header("file Manager")
    st.write(st.session_state)
    
    storage_path_obj = Path(storage_path)
    files = list_files(storage_path_obj)
    if files:
        i= 0
        for file in files:
            col1, col2, col3,col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(file.name)
            with col2:
                st.write(f"{os.path.getsize(file) / 1024:.2f} KB")
            with col3:
                st.download_button(
                    label="Download",
                    data=open(file, "rb").read(),
                    file_name=file.name,
                    mime='text/plain'
                )
            with col4:
                del_button = st.button("Delete", key=i) # key=file.name
                if del_button:
                    delete_file(file)
                    st.session_state.pop(file.name)
                    st.success(f"{file.name} deleted successfully.")
                    st.rerun()  # Refresh the app to show updated file list
            
            with st.expander(f"preview: {file.name}"):
                try:
                    df = pd.read_csv(file)
                    st.dataframe(df.head(5))

                except Exception as e:
                    st.error(f"Error reading {file}: {e}")
            
            i+=1
                
    else:
        st.write("No files found.")
