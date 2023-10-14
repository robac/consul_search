def get_consul_kv_path(config, suffix):
    return f"http://{config['CONSUL_PATH']}:{config['CONSUL_PORT']}/ui/cecolo/kv/{suffix}/edit"