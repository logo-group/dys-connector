import os
from unittest import TestCase
from dys_connector.dys_api_manager import DYSManager

DYS_ENDPOINT = os.environ['DYS_ENDPOINT']
DYS_TOKEN = os.environ['DYS_TOKEN']
DYS_CLEAR_DIR = os.environ['DYS_CLEAR_DIR']
DOC_CID = os.environ['DOC_CID']


class TestIntegration(TestCase):
    def test_generate_external_share(self):
        manager = DYSManager(DYS_ENDPOINT, DYS_TOKEN)
        external_url = manager.generate_external_share(DOC_CID)
        self.assertIn(DOC_CID, external_url)

    def test_clear_directory(self):
        manager = DYSManager(DYS_ENDPOINT, DYS_TOKEN)
        manager.clear_directory(DYS_CLEAR_DIR)
        dir_list = manager.get_dir_structure(DYS_CLEAR_DIR)
        self.assertEqual(dir_list, [])
