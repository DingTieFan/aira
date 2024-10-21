import streamlit as st

# 定义页面
def main_page():
    st.title("主页面")
    st.write("这是主页面的内容。")

def loan_count_trend_page():
    st.title("近30日放款笔数趋势")
    # 在此处添加数据计算和图表生成代码
    st.page_link('loan_count_trend_page.py')

# 创建页面对象
main = st.Page(main_page, title="主页面", icon="🏠")
loan_count_trend = st.Page(loan_count_trend_page, title="放款笔数趋势", icon="🏠")

# 设置导航
pg = st.navigation([main, loan_count_trend])

# 运行应用
pg.run()
