import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from consul_tools.ConsulSearch import ConsulSearch, SearchOptions
from consul_tools import utils
from st_aggrid.shared import GridUpdateMode, ColumnsAutoSizeMode
import yaml
import logging

CONFIG_MANDATORY_ITEMS = ["host", "port", "edit-url", "encoding"]
CONFIG_FILE = "config.yaml"

@st.cache_data
def load_consul_configs(path):
    config, lst = None, None
    try:
        with open(path, 'r') as file:
            config = yaml.safe_load(file)
        lst = [item for item in config]
    except:
        logging.error("Can't load config file %s", path)

    error = False
    for instance_name, instance in config.items():
        for item in CONFIG_MANDATORY_ITEMS:
            if item not in instance:
                error = True
                logging.error("Missing item in config file. Instance: %s, item: %s", instance_name, item)
    if error:
        return None, None
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
    try:
        logging.info(f"loading instance {instance}")
        data = ConsulSearch()
        data.load_data(get_config(config, instance))
        logging.info(f"loaded instance {instance}, number of items {len(data.consul_data)}")
        return data
    except:
        return None

@st.cache_data(hash_funcs={ConsulSearch: lambda p: p.last_update})
def load_results(text, instance : ConsulSearch, instance_name : str, options : SearchOptions):
    print(instance)
    return instance.search([text], options)

def output_page():
    st.header('Consul search', divider='blue')

    if config is None or consul_list is None:
        st.write("Error loading the config file!")
        return

    instance_name = st.selectbox("Consul instance:", consul_list)
    title = st.text_input("Text", "")
    use_regular = st.checkbox("regular expression", value=False)
    search_keys = st.checkbox("search in keys", value=True)
    search_values = st.checkbox("search in values", value=True)
    search_ins = load_consul_data(config, instance_name)


    if (len(title.strip()) > 2) and (search_keys or search_values):
        options = SearchOptions(search_keys, search_values, use_regular, "")
        data = load_results(title, search_ins, instance_name, options)
        if data is not None and len(data) > 0:
            selection = aggrid_interactive_table(data)
            if selection and len(selection["selected_rows"]) > 0:
                st.write(utils.get_consul_kv_path(get_config(config, instance_name), selection["selected_rows"][0]["key"]))
                st.code(selection["selected_rows"][0]["value"], line_numbers=True)
        else:
            st.write(f"*:red[**no data** for input \"{title}\"]*")
    else:
        st.write(
            "*:blue[There should be at least two characters in the Text field and \"search in keys\" or \"search in values\" enabled.]*")


st.set_page_config(layout="wide")
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
config, consul_list = load_consul_configs(CONFIG_FILE)
output_page()



