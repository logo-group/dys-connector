import os
from dys_connector.dys_api_manager import DYSManager

DYS_ENDPOINT = os.environ['DYS_ENDPOINT']
DYS_TOKEN = os.environ['DYS_TOKEN']
DYS_CLEAR_DIR = os.environ['DYS_CLEAR_DIR']


def test_clear_directory():
    manager = DYSManager(DYS_ENDPOINT, DYS_TOKEN)
    manager.clear_directory(DYS_CLEAR_DIR)
    dir_list = manager.get_dir_structure(DYS_CLEAR_DIR)
    assert dir_list == []
