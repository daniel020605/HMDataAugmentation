import configparser

config_path = './config.ini'

def read_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config


def get_database_config():
    # 读取配置文件
    config = read_config(config_path)

    # 访问配置项
    database_host = config['database']['host']
    database_user = config['database']['user']
    database_password = config['database']['password']
    database_name = config['database']['name']

    return database_host, database_user, database_password, database_name

def get_llm_config():
    # 读取配置文件
    config = read_config(config_path)

    llm_url = config['llm']['url']
    token = config['llm']['access_token']

    return llm_url, token

if __name__ == '__main__':
    print(get_database_config())