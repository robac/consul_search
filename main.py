import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from consul_tools.ConsulSearch import ConsulSearch, SearchOptions
from consul_tools import utils
from st_aggrid.shared import GridUpdateMode, DataReturnMode, JsCode, walk_gridOptions, ColumnsAutoSizeMode, AgGridTheme, ExcelExportMode
import yaml

@st.cache_data
def load_consul_configs(path):
    config = None
    with open(path, 'r') as file:
        config = yaml.safe_load(file)

    lst = [item for item in config]
    return config, lst


def get_config(config, instance):
    return config[instance]

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
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        height=500
    )

    return selection

@st.cache_data
def load_consul_data(config, instance):
    print(f"loading instance {instance}")
    data = ConsulSearch()
    data.load_data(get_config(config, instance))
    print ("loading instance size ", len(data.consul_data))
    return data

@st.cache_data
def load_results(text, instance, options : SearchOptions):
    return search_ins.search([text], options)

st.set_page_config(layout="wide")

config, consul_list = load_consul_configs('config.yaml')

st.header('Consul search', divider='blue')
instance = st.selectbox('Consul instance:', consul_list)
title = st.text_input('Text', '')
use_regular = st.checkbox('regular expression', value=False)
search_keys = st.checkbox('search in keys', value=True)
search_values = st.checkbox('search in values', value=True)
search_ins = load_consul_data(config, instance)

if (len(title.strip()) > 2) and (search_keys or search_values):
    options = SearchOptions(search_keys, search_values, use_regular, "")
    data = load_results(title, instance, options)
    if data is not None and len(data) > 0:
        selection = aggrid_interactive_table(data)
        if selection and len(selection["selected_rows"]) > 0:
            st.write(utils.get_consul_kv_path(get_config(config, instance), selection["selected_rows"][0]["key"]))
            st.code(selection["selected_rows"][0]["value"], line_numbers=True)
    else:
        st.write(f":red[**no data** for input: {title}]")
else:
    st.write("*:blue[There should be at least two characters in Text and \"search in keys\" or \"search in values\" enabled.]*")