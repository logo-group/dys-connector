from dys_connector.dys_api_manager import DYSManager

manager = DYSManager("dys-endpoint", "token")


def test_copy_document(mocker):

    def mock_copy_document(self, doc_cid: str, parent_folder_cid: str = None, x_lang: str = None,
                           add_copy_of_prefix: bool = False):
        if add_copy_of_prefix:
            if "en_US" in x_lang:
                return {"status_code": 200, "text": "Copy of document.html"}
            elif "tr_TR" in x_lang:
                return {"status_code": 200, "text": "document.html - Kopya"}
        else:
            return {"status_code": 200, "text": "document.html"}

    mocker.patch(
        'dys_connector.dys_api_manager.DYSManager.copy_document',
        mock_copy_document
    )

    res = manager.copy_document("cid", "parent", "en_US", True)
    assert res["status_code"] == 200
    assert res["text"] == "Copy of document.html"

    res = manager.copy_document("cid", "parent", "tr_TR", True)
    assert res["status_code"] == 200
    assert res["text"] == "document.html - Kopya"

    res = manager.copy_document("cid", "parent")
    assert res["status_code"] == 200
    assert res["text"] == "document.html"
