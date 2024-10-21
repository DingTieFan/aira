import streamlit as st

def show_main_page():
    st.title("主页面")
    st.write("欢迎来到贷款分析Dashboard的主页面！")
    
    # 示例数据展示或其他内容
    st.subheader("一些示例内容")
    st.write("此页面可以包含业务总览、其他分析内容等。")
    
    # 示例图表
    st.line_chart([1, 2, 3, 4, 5, 6])
