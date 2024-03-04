import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from consul_tools.ConsulSearch import ConsulSearch, SearchOptions
from consul_tools import utils

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
    options.configure_auto_height(autoHeight=False)
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="material",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
        height=500
    )

    return selection


@st.cache_data
def load_results(text, options : SearchOptions):
    return search_ins.search([text], options)

search_ins = ConsulSearch()
search_ins.load_data(get_config())

st.set_page_config(layout="wide")
st.header('Consul search', divider='blue')
title = st.text_input('Text', '')
keys = st.checkbox('search in keys', value=True)
values = st.checkbox('search in values', value=True)
if len(title) > 0:
    options = SearchOptions(keys, values, "")
    data = load_results(title, options)
    if data is not None and len(data) > 0:
        selection = aggrid_interactive_table(data)
        if selection and len(selection["selected_rows"]) > 0:
            st.write(utils.get_consul_kv_path(get_config(), selection["selected_rows"][0]["key"]))
            st.code(selection["selected_rows"][0]["value"])
    else:
        st.write("**no data**")
