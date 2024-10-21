import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import pandas as pd

st.set_page_config(layout="wide")
st.title('Tesla Stock Volume Analysis')

DATA_FILE = 'data/df_group.csv'
df = pd.read_csv(DATA_FILE)
new_dfs, code = spreadsheet(df)

st.write(new_dfs)
st.code(code)