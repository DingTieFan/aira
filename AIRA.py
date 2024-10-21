# 利用streamlit生成3个横向页面，分别为：chat、analytics、dashboard。其中：chat页面用于用户通过输入文本与机器人进行交互，进行数据分析，analytics页面用于展示传统BI报表中的分析方法，dashboard页面用于展示前面2个页面的结果进行可视化。
import streamlit as st
import os 
from pathlib import Path
import pandas as pd
from utils.data_helper import list_files

st.set_page_config(
    page_title="AI Risk Analytics",
    page_icon="👋",
)

storage_path = Path('data/uploaded_files')
if not os.path.exists(storage_path):
    os.makedirs(storage_path)

if 'storage_path' not in st.session_state:
    st.session_state['storage_path'] = 'data/uploaded_files'

files = list_files(storage_path)

for file in files:
    st.session_state[file.name] = '{}/{}'.format(storage_path, file.name)

standard_files_name = ['loan_table.csv', 'repayment_table.csv', 'performance_table.csv']

def check_standard_files(standard_files_name):
    is_standard = []
    for name in standard_files_name:
        if name in st.session_state.keys():
            is_standard.append(True)
    
    return all(is_standard)
    
aa = check_standard_files(standard_files_name)
if not check_standard_files(standard_files_name):
    st.write("No files found in storage path.")
    st.page_link("pages/4_🔎_Data.py", label="Data Manager", icon="🔎")
else:
    st.page_link("pages/1_🧊_Chat.py", label="1_🧊_Chat", icon="1️⃣")
    st.page_link("pages/2_📈_Analytics.py", label="2_📈_Analytics", icon="2️⃣")
    st.page_link("pages/3_📊_Dashboard.py", label="3_📊_Dashboard", icon="3️⃣")


# st.write("# Welcome to Streamlit! 👋")

# st.sidebar.success("Select a demo above.")


# st.page_link("AIRA.py", label="Home", icon="🏠")
# st.page_link("pages/1_🧊_Chat.py", label="1_🧊_Chat", icon="1️⃣")
# st.page_link("pages/2_📈_Analytics.py", label="2_📈_Analytics", icon="2️⃣")
# st.page_link("pages/3_📊_Dashboard.py", label="3_📊_Dashboard", icon="3️⃣")
# st.page_link("pages/4_🔎_Data.py", label="4_🔎_Data", icon="4️⃣")


# st.markdown(
#     """
#     AIRA: AI Risk Analytics: a comprehensive solution designed to enhance your risk management processes. 
#     AIRA features an intuitive data analytics chatbox that allows users to interact with data in real-time, facilitating quick insights and decision-making. 
#     Our advanced business intelligence tools provide in-depth analysis and reporting capabilities, enabling users to visualize trends and patterns effortlessly. 
#     Additionally, the integrated dashboard presents a centralized view of key metrics and performance indicators, making it easier to monitor and assess risk across your organization. 
#     Experience the power of AI-driven analytics with AIRA and transform your approach to risk management.
# """
# )