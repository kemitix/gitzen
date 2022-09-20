import yaml


def read(file_name):
    with open(file_name, "r") as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)
