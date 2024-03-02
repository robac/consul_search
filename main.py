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
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

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


st.header('Consul search', divider='blue')
title = st.text_input('Text', '')
keys = st.checkbox('search in keys', value=True)
values = st.checkbox('search in values', value=True)
if len(title) > 0:
    search_ins = ConsulSearch()
    search_ins.load_data(get_config())
    data = search_ins.search([title])
    df = pd.DataFrame(data=data)
    selection = aggrid_interactive_table(df)
    st.write("hotovo")
