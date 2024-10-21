import streamlit as st
import pandas as pd

# 示例数据
data = {
    '日期': pd.date_range(start='2020-01-01', periods=100),
    '值': range(100)
}
df = pd.DataFrame(data)

# 转换日期为字符串
date_options = df['日期'].dt.strftime('%Y-%m-%d').tolist()

# 使用 select_slider 选择日期范围
selected_dates = st.select_slider(
    "选择日期范围",
    options=date_options,
    value=(date_options[0], date_options[-1])
)

# 筛选数据
start_date, end_date = pd.to_datetime(selected_dates)
filtered_data = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]

# 显示筛选后的数据
st.write(filtered_data)
