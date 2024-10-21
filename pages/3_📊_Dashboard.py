#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from utils.data_helper import vintage, days_difference, cur_overdue_days
import numpy as np

#######################
# Page configuration
st.set_page_config(
    page_title="Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
# Load data
# DATA_FILE = 'data/df_group.csv'
# df = pd.read_csv(DATA_FILE)

storage_path = st.session_state.get('storage_path')
performance_table_name = 'performance_table.csv'
loan_table_name = 'loan_table.csv'
repayment_table_name = 'repayment_table.csv'

@st.cache_data  # 👈 添加缓存装饰器
def load_data(url):
    df = pd.read_csv(url)
    return df

#######################
# Sidebar
with st.sidebar:
    page = st.sidebar.radio("Select Dashboard", ["Overview", "Aquisition", "Customer Management", "Collection & Recovery"])


#######################
if page == "Overview":
    st.header("Overview")

    if performance_table_name not in st.session_state or loan_table_name not in st.session_state or repayment_table_name not in st.session_state:
        st.write("Please upload {}、{}、{} csv file first.".format(loan_table_name, repayment_table_name, performance_table_name))
        st.page_link("pages/4_🔎_Data.py", label="Data", icon="🔎")
    
    else:
        p_df = load_data(st.session_state.get(performance_table_name))                # Use vectorized string operations
        p_df['放款月份'] = p_df['放款日期'].str[:7]
        p_df['统计月份'] = p_df['统计日期'].str[:7]

        # Direct calculations using vectorized operations
        p_df['NCO'] = p_df['坏账核销金额'] - p_df['坏账回收金额']
        p_df['DPD30+'] = p_df[[f'余额M{i}' for i in range(2, 8)]].sum(axis=1)
        p_df['不含M7余额'] = p_df[[f'余额M{i}' for i in range(1, 7)] + ['正常余额']].sum(axis=1)
        p_df['上月余额'] = p_df[[f'上月余额M{i}' for i in range(1, 8)] + ['上月正常余额']].sum(axis=1)

        with st.container():
            st.write("Vintage")
            with st.expander("编辑和筛选图表"):
                # 筛选日期范围
                # 数据筛选框
                loan_term = st.selectbox("放款期限", options=pd.Series(p_df['放款期限'].unique()).sort_values().to_list(), index=None)
                loan_type = st.selectbox("借款类型", options=p_df['借款类型'].unique().tolist(), index=None)
                initial_rating = st.selectbox("初始评级", options=p_df['初始评级'].unique().tolist(), index=None)

            vintage_df = vintage(p_df, loan_term, loan_type, initial_rating)
            new_data2 = {}
            mobs = vintage_df.columns.tolist()
            new_data2['MOB'] = mobs
            for i in vintage_df.index:
                new_data2[i] = vintage_df.loc[i].values.tolist()

            plot_df = pd.DataFrame(data=new_data2)
            st.line_chart(plot_df, x='MOB', y=plot_df.columns[1:].tolist())
        
        with st.container():
            st.write("DQ Rate")

            with st.expander("编辑和筛选图表"):
                sorted_months = sorted(p_df['放款月份'].unique())

                # 使用 select_slider 选择日期范围
                selected_dates = st.select_slider(
                    "选择日期范围",
                    options=sorted_months,
                    value=(sorted_months[0], sorted_months[-1]),
                    key='date_range1'
                )
            
            filter_df = p_df
            if selected_dates:
                st.write(f"Selected month: {selected_dates}")

                filter_df = p_df[(p_df['放款月份'] >= selected_dates[0]) & (p_df['放款月份'] <= selected_dates[1])]

            # 聚合数据并计算比率
            agg_df = filter_df.groupby('统计月份').agg({
                'DPD30+': 'sum',
                '放款金额': 'sum'
            }).reset_index()

            # 计算比率
            agg_df['rate'] = agg_df['DPD30+'] / agg_df['放款金额']

            # 绘图
            st.bar_chart(agg_df[['统计月份', 'rate']], x='统计月份', y='rate')

        with st.container():
            st.write("Net Charge Off")

            with st.expander("编辑和筛选图表"):
                # fk_mths = pd.to_datetime(p_df['放款月份'], format='%Y-%m')  # 根据实际格式调整
                sorted_months = sorted(p_df['放款月份'].unique())

                # 使用 select_slider 选择日期范围
                selected_dates = st.select_slider(
                    "选择日期范围",
                    options=sorted_months,
                    value=(sorted_months[0], sorted_months[-1]),
                    key='date_range2'
                )
            
            filter_df = p_df
            if selected_dates:
                st.write(f"Selected month: {selected_dates}")

                filter_df = p_df[(p_df['放款月份'] >= selected_dates[0]) & (p_df['放款月份'] <= selected_dates[1])]

            # 聚合数据并计算比率
            agg_df = filter_df.groupby('统计月份').agg({
                'NCO': 'sum',
                '不含M7余额': 'sum'
            }).reset_index()

            # 直接计算比率
            agg_df['rate'] = (agg_df['NCO'] / agg_df['不含M7余额']) * 12

            # 绘图
            st.bar_chart(agg_df[['统计月份', 'rate']], x='统计月份', y='rate')



        with st.container():
            st.write("Net Interest Margin")

            with st.expander("编辑和筛选图表"):
                # fk_mths = pd.to_datetime(p_df['放款月份'], format='%Y-%m')  # 根据实际格式调整
                sorted_months = sorted(p_df['放款月份'].unique())

                # 使用 select_slider 选择日期范围
                selected_dates = st.select_slider(
                    "选择日期范围",
                    options=sorted_months,
                    value=(sorted_months[0], sorted_months[-1]),
                    key='date_range3'
                )
            
            filter_df = p_df
            if selected_dates:
                st.write(f"Selected month: {selected_dates}")

                filter_df = p_df[(p_df['放款月份'] >= selected_dates[0]) & (p_df['放款月份'] <= selected_dates[1])]            

            # 聚合并计算比率
            agg_df = filter_df.groupby('统计月份').agg({
                '实还利息': 'sum',
                '不含M7余额': 'sum'
            }).reset_index()

            # 直接计算比率
            agg_df['rate'] = (agg_df['实还利息'] / agg_df['不含M7余额']) * 12 - 0.05

            # 绘图
            st.bar_chart(agg_df[['统计月份', 'rate']], x='统计月份', y='rate')


        with st.container():
            st.write("Return on Asset")

            with st.expander("编辑和筛选图表"):
                # fk_mths = pd.to_datetime(p_df['放款月份'], format='%Y-%m')  # 根据实际格式调整
                sorted_months = sorted(p_df['放款月份'].unique())

                # 使用 select_slider 选择日期范围
                selected_dates = st.select_slider(
                    "选择日期范围",
                    options=sorted_months,
                    value=(sorted_months[0], sorted_months[-1]),
                    key='date_range4'
                )
            
            filter_df = p_df
            if selected_dates:
                st.write(f"Selected month: {selected_dates}")

                filter_df = p_df[(p_df['放款月份'] >= selected_dates[0]) & (p_df['放款月份'] <= selected_dates[1])]

            # 聚合数据
            agg_df = filter_df.groupby('统计月份').agg({
                '实还利息': 'sum',
                'NCO': 'sum',
                '不含M7余额': 'sum'
            }).reset_index()

            # 使用NumPy计算ROA
            not_m7_balance = agg_df['不含M7余额'].values
            roa = (agg_df['实还利息'].values / not_m7_balance) * 12 - 0.05 - \
                (agg_df['NCO'].values / not_m7_balance) * 12 - 0.04

            # 创建结果DataFrame
            roa_df = pd.DataFrame({'ROA': roa, '统计月份': agg_df['统计月份']})

            # 绘图
            st.bar_chart(roa_df, x='统计月份', y='ROA')

if page == "Aquisition":
    st.header("Aquisition")

    

if page == "Customer Management":
    st.header("Customer Management")
    st.write("这是 Customer Management 页的内容。")


if page == "Collection & Recovery":
    st.header("Collection & Recovery")

    if performance_table_name not in st.session_state or loan_table_name not in st.session_state or repayment_table_name not in st.session_state:
        st.write("Please upload {}、{}、{} csv file first.".format(loan_table_name, repayment_table_name, performance_table_name))
        st.page_link("pages/4_🔎_Data.py", label="Data", icon="🔎")
    
    else:
        p_df = load_data(st.session_state.get(performance_table_name))                # Use vectorized string operations
        p_df['放款月份'] = p_df['放款日期'].str[:7]
        p_df['统计月份'] = p_df['统计日期'].str[:7]
        p_df['上月余额'] = p_df[[f'上月余额M{i}' for i in range(1, 8)] + ['上月正常余额']].sum(axis=1)

        repay_df = load_data(st.session_state.get(repayment_table_name))
        repay_df['应还月份'] = repay_df['应还时间'].str[:7]
        repay_df['实还月份'] = repay_df['实还时间'].str[:7]

        repay_df['应还时间'] = pd.to_datetime(repay_df['应还时间'], errors='coerce')
        repay_df['实还时间'] = pd.to_datetime(repay_df['实还时间'], errors='coerce')
        repay_df['迟还天数'] = (repay_df['实还时间'] - repay_df['应还时间']).dt.days


        with st.container():
            st.write("C-M1")

            with st.expander("编辑和筛选图表"):
                # fk_mths = pd.to_datetime(p_df['放款月份'], format='%Y-%m')  # 根据实际格式调整
                sorted_months = sorted(p_df['放款月份'].unique())

                # 使用 select_slider 选择日期范围
                selected_dates = st.select_slider(
                    "选择日期范围",
                    options=sorted_months,
                    value=(sorted_months[0], sorted_months[-1]),
                    key='date_range1'
                )
            
            filter_df = p_df
            if selected_dates:
                st.write(f"Selected month: {selected_dates}")

                filter_df = p_df[(p_df['放款月份'] >= selected_dates[0]) & (p_df['放款月份'] <= selected_dates[1])]   
            
            filter_df['temp_余额M1'] = filter_df[['上月正常余额', '余额M1']].apply(lambda x: x['余额M1'] if x['上月正常余额'] > 0 else 0, axis=1)
            
            d1 = filter_df.groupby('统计月份').agg({'temp_余额M1': 'sum'}).reset_index()
            d2 = filter_df.groupby('统计月份').agg({'上月正常余额': 'sum'}).reset_index()

            c_m1 = d1.merge(d2, how='inner', right_on='统计月份', left_on='统计月份')
            c_m1['rate'] = c_m1['temp_余额M1'] / c_m1['上月正常余额']

            st.bar_chart(c_m1[['统计月份', 'rate']], x='统计月份', y='rate')

        with st.container():
            st.write("首逾&首逾3+")

            filter_df = repay_df[repay_df['期数'] == 1 ]
            filter_df['temp_首逾'] = filter_df[['迟还天数']].apply(lambda x: 1 if x['迟还天数'] > 0 else 0, axis=1)
            filter_df['temp_首逾3+'] = filter_df[['迟还天数']].apply(lambda x: 1 if x['迟还天数'] >= 3 else 0, axis=1)

            d1 = filter_df.groupby('应还月份').agg({'temp_首逾': 'sum'}).reset_index()
            d2 = filter_df.groupby('应还月份').agg({'temp_首逾3+': 'sum'}).reset_index()
            d3 = filter_df.groupby('应还月份').agg({'借据号': 'nunique'}).reset_index()

            first_overdue = d1.merge(d3, how='inner', right_on='应还月份', left_on='应还月份')
            first_overdue_3plus = d2.merge(d3, how='inner', right_on='应还月份', left_on='应还月份')
            first_overdue['rate'] = first_overdue['temp_首逾'] / first_overdue['借据号']
            first_overdue_3plus['rate'] = first_overdue_3plus['temp_首逾3+'] / first_overdue_3plus['借据号']

            st.bar_chart(first_overdue[['应还月份', 'rate']], x='应还月份', y='rate')
            st.bar_chart(first_overdue_3plus[['应还月份', 'rate']], x='应还月份', y='rate')





        