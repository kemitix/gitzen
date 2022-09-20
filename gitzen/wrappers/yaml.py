import yaml

from gitzen import file


def read(file_env: file.Env, file_name: str):
    with file.io_read(file_env, file_name) as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)
