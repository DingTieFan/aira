import streamlit as st
import pandas as pd
from langchain_groq import ChatGroq
from pandasai import Agent
import uuid

storage_path = st.session_state.get('storage_path')

file_name = 'performance_table.csv' 

# 判断是否为字符串类型
def is_string(obj):
    return isinstance(obj, str)

# 判断字符串是否是图片格式类型（常见的图片格式有：JPEG, PNG, GIF, BMP 等）
def is_image_format(string):
    lowercase_string = string.lower()
    return any(lowercase_string.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp'])

def is_dataframe(obj):
    return isinstance(obj, pd.DataFrame)

def show_result(response):
    if is_dataframe(response):
        st.dataframe(response)
    elif is_string(response) and is_image_format(response):
        st.image(response)
    else:
        st.write(response)
def show_hci():
    """
    人机交互的，如果计算结果错误，自动识别是否存在工具；如存在就尝试推荐工具；如不存在，记录下来.            
    """
    st.text("以上答案是否正确？如不正确，进行如下操作......")
    col1, col2 = st.columns([1, 1])  # 这里可以通过设置比例来调整每个列的宽度
    with col1:
        st.page_link("pages/2_📈_Analytics.py", label="Analytics Tools", icon="📈")

    with col2:
        st.feedback(options="thumbs", key=str(uuid.uuid4()))

def get_agent(data,llm):
    """
    The function creates an agent on the dataframes exctracted from the uploaded files
    Args: 
        data: A Dictionary with the dataframes extracted from the uploaded data
        llm:  llm object based on the ll type selected
    Output: PandasAI Agent
    """
    agent = Agent(data, config = {"llm":llm, "verbose": True, "open_charts": False}) 

    return agent


def chat_window(analyst):
    with st.chat_message("assistant"):
        st.text("Explore your data with AIRA?🧐")

    #Initilizing message history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    #Displaying the message history on re-reun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            #priting the questions
            if 'question' in message:
                st.markdown(message["question"])
            #printing the code generated and the evaluated code
            elif 'response' in message:
                #getting the response
                #st.write(message['response'])
                show_result(message['response'])
                show_hci()
            #retrieving error messages
            elif 'error' in message:
                st.text(message['error'])
    #Getting the questions from the users
    user_question = st.chat_input("What are you curious about? ")

    if user_question:
        #Displaying the user question in the chat message
        with st.chat_message("user"):
            st.markdown(user_question)
        #Adding user question to chat history
        st.session_state.messages.append({"role":"user", "question":user_question})
       
        try:
            with st.spinner("Analyzing..."):
                response = analyst.chat(user_question)
                show_result(response)
                show_hci()

                st.session_state.messages.append({"role":"assistant", "response": response})
        
        except Exception as e:
            st.write(e)
            error_message = "⚠️Sorry, Couldn't generate the answer! Please try rephrasing your question!"

    #Function to clear history
    def clear_chat_history():
        st.session_state.messages = []

    #Button for clearing history
    st.sidebar.text("Click to Clear Chat history")
    st.sidebar.button("CLEAR 🗑️",on_click=clear_chat_history)

@st.cache_data  # 👈 添加缓存装饰器
def load_data(url):
    df = pd.read_csv(url)
    return df

#####################################################页面###################################################################################
st.set_page_config(page_title="Data Analyst", page_icon="chart_with_upwards_trend")
st.title(':blue[Data Analysis ] :red[Chatbot]')

#Side Menu Bar
with st.sidebar:
    st.title("Configuration:⚙️")
    
    
df = pd.DataFrame()
st.text("Welcome to the Data Analyst Chatbot, Let's start with the data you need!")
with st.expander("✨ Data Manager"):
    if file_name not in st.session_state:
        st.write("Please upload {} csv file first.".format(file_name))
        st.page_link("pages/4_🔎_Data.py", label="Data", icon="🔎")
    else:
        DATA_FILE = '{}/{}'.format(storage_path, file_name)
        df = load_data(DATA_FILE)
        st.write(df.head(5))

llm = ChatGroq(
                model="llama3-70b-8192",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                # other params...
            )

analyst = get_agent(df, llm)
chat_window(analyst)