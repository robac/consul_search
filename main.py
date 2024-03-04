import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from consul_tools.ConsulSearch import ConsulSearch, SearchOptions
from consul_tools import utils
from streamlit_searchbox import st_searchbox
import yaml

@st.cache_data
def load_consul_configs(path):
    config = None
    with open(path, 'r') as file:
        config = yaml.safe_load(file)

    lst = [item for item in config]
    return config, lst


def get_config(config, instance):
    return {
        "CONSUL_PATH" : config[instance]["host"],
        "CONSUL_PORT" : config[instance]["port"],
        "CONSUL_ENCODING" : config[instance]["encoding"],
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
def load_consul_data(config, instance):
    print(instance)
    data = ConsulSearch()
    print(get_config(config, instance))
    data.load_data(get_config(config, instance))
    return data

@st.cache_data
def load_results(text, options : SearchOptions):
    return search_ins.search([text], options)

st.set_page_config(layout="wide")

config, consul_list = load_consul_configs('config.yaml')
st.code(consul_list)


st.header('Consul search', divider='blue')
title = st.text_input('Text', '')
use_regular = st.checkbox('regular expression', value=False)
search_keys = st.checkbox('search in keys', value=True)
search_values = st.checkbox('search in values', value=True)
instance = st.selectbox('Select Consul instance:', consul_list)
search_ins = load_consul_data(config, instance)

if len(title) > 0:
    options = SearchOptions(search_keys, search_values, use_regular, "")
    data = load_results(title, options)
    if data is not None and len(data) > 0:
        selection = aggrid_interactive_table(data)
        if selection and len(selection["selected_rows"]) > 0:
            st.write(utils.get_consul_kv_path(get_config(config, instance), selection["selected_rows"][0]["key"]))
            st.code(selection["selected_rows"][0]["value"], line_numbers=True)
    else:
        st.write("**no data**")
