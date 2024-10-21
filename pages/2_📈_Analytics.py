import streamlit as st
from streamlit_echarts import st_echarts
import pandas as pd
import numpy as np
from utils.data_helper import vintage

# 示例数据
# 加载数据
storage_path = st.session_state.get('storage_path')

performance_table_name = 'performance_table.csv'
loan_table_name = 'loan_table.csv'
repayment_table_name = 'repayment_table.csv'

@st.cache_data  # 👈 添加缓存装饰器
def load_data(url):
    df = pd.read_csv(url)
    return df


def filter(loan_term, loan_type, initial_rating):
     #过滤数据
    filtered_df = df.copy()

    if loan_term:
        filtered_df = filtered_df[filtered_df['Loan Term'] == loan_term]
    if loan_type:
        filtered_df = filtered_df[filtered_df['Loan Type'] == loan_type]
    if initial_rating:
        filtered_df = filtered_df[filtered_df['Initial Rating'] == initial_rating]
    
    return filtered_df



# 在侧栏选择标签页
page = st.sidebar.radio("Select an analysis method", ["Vintage Analytics", "Portfolio Analytics", "Flow Rate", "FPD"])

# 根据选择加载相应的内容
if page == "Vintage Analytics":
    st.header("Vintage Analytics")
    
    if performance_table_name not in st.session_state:
        st.write('请上传文件，生成preformance_table.csv!!')
        st.page_link("pages/4_🔎_Data.py", label="Data", icon="🔎")
    else:
        df = load_data(st.session_state.get(performance_table_name))
        # 数据筛选框
        loan_term = st.selectbox("放款期限", options=pd.Series(df['放款期限'].unique()).sort_values().to_list(), index=None)
        loan_type = st.selectbox("借款类型", options=df['借款类型'].unique().tolist(), index=None)
        initial_rating = st.selectbox("初始评级", options=df['初始评级'].unique().tolist(), index=None)

        # print(loan_term, loan_type, initial_rating)

        # 根据选择过滤数据
        vintage_df = vintage(df, loan_term, loan_type, initial_rating)
        
        # 数据格式转换
        new_data1 = {}
        new_data1[vintage_df.index.name] = vintage_df.index.values
        for i in range(vintage_df.shape[1]):
            new_data1['mob{}'.format(i)] = vintage_df.iloc[:, i].values

        filtered_data = pd.DataFrame(data=new_data1)
        # 数据图形展示
        new_data2 = {}
        mobs = vintage_df.columns.tolist()
        new_data2['MOB'] = mobs
        for i in vintage_df.index:
            new_data2[i] = vintage_df.loc[i].values.tolist()

        plot_df = pd.DataFrame(data=new_data2)
        st.line_chart(plot_df, x='MOB', y=plot_df.columns[1:].tolist())
        # # 数据表格展示
        st.dataframe(filtered_data, use_container_width=True, hide_index=True)
    
    

elif page == "Portfolio Analytics":
    st.header("Portfolio Analytics")
    st.write("这是 Portfolio Analytics 页的内容。")

elif page == "Flow Rate":
    st.header("Flow Rate")
    st.write("这是 Flow Rate 页的内容。")

elif page == "FPD":
    st.header("FPD")
    st.write("这是 FPD 页的内容。")
