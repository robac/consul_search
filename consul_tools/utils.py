def get_consul_kv_path(config, suffix):
    return config["edit-url"].format(suffix=suffix)