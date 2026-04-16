from .config import conf as base_conf

class local_conf(base_conf):
    db_password = "Dean1996!"
    db_host = base_conf.db_host
    db_name = base_conf.db_name
    db_port = base_conf.db_port
    db_user = base_conf.db_user
    app_host = base_conf.app_host
    app_port = base_conf.app_port