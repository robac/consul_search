import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from consul_tools.ConsulSearch import ConsulSearch

def get_config():
    return {
        "CONSUL_PATH" : r"consul.consul-1.cecolo.gofg.net",
        "CONSUL_PORT" : 8500,
        "CONSUL_ENCODING" : "UTF-8",
        "SEARCH_RECURSE" : True,
        "SEARCH_INDEX" : ""
    }

def aggrid_interactive_table(df: pd.DataFrame):
    options = GridOptionsBuilder.from_dataframe(
        df
    )

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="alpine",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection


@st.cache_data
def load_results(text):
    return search_ins.search([text])

search_ins = ConsulSearch()
search_ins.load_data(get_config())

st.header('Consul search', divider='blue')
title = st.text_input('Text', '')
keys = st.checkbox('search in keys', value=True)
values = st.checkbox('search in values', value=True)
if len(title) > 0:
    data = load_results(title)
    if len(data) > 0:
        selection = aggrid_interactive_table(data)
        if selection and len(selection["selected_rows"]) > 0:
            st.write(selection["selected_rows"][0]["key"])
            st.write(selection["selected_rows"][0]["value"])
    else:
        st.write("**no data**")
