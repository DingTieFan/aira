import streamlit as st
import pandas as pd
import numpy as np

def show_loan_count_trend_page():
    st.title("近30日放款笔数趋势")

    # 模拟数据生成（实际使用中可以替换为上传或读取的文件）
    np.random.seed(42)
    dates = pd.date_range('2023-09-01', periods=60)
    loan_count = np.random.randint(35, 45, size=60)

    data = pd.DataFrame({
        'date': dates,
        'loan_count': loan_count
    })

    # 计算近30日放款笔数
    data['30_day_sum'] = data['loan_count'].rolling(window=30).sum()

    # 显示计算的DataFrame（可选）
    st.write("近30日放款笔数数据表：")
    st.dataframe(data)

    # 图表展示
    st.subheader("近30日放款笔数趋势图")
    st.line_chart(data.set_index('date')['30_day_sum'])

    # 图表编辑功能：用户可选择显示的日期范围和图表类型
    with st.expander("编辑和筛选图表"):
        # 筛选日期范围
        date_range = st.slider("选择日期范围", 0, len(data) - 1, (0, len(data) - 1))
        filtered_data = data.iloc[date_range[0]:date_range[1] + 1]

        # 选择图表类型
        chart_type = st.selectbox("选择图表类型", ['折线图', '柱状图'])

        # 根据图表类型显示数据
        if chart_type == '折线图':
            st.line_chart(filtered_data.set_index('date')['30_day_sum'])
        elif chart_type == '柱状图':
            st.bar_chart(filtered_data.set_index('date')['30_day_sum'])
