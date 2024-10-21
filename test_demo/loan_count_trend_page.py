import pandas as pd
import numpy as np
import streamlit as st


# 模拟数据
np.random.seed(42)
dates = pd.date_range('2023-09-01', periods=60)
loan_count = np.random.randint(35, 45, size=60)

data = pd.DataFrame({
    'date': dates,
    'loan_count': loan_count
})

# 计算近30日放款笔数
data['30_day_sum'] = data['loan_count'].rolling(window=30).sum()

# 绘制线图
st.line_chart(data.set_index('date')['30_day_sum'])