from dys_connector.dys_api_manager import DYSManager

manager = DYSManager("dys-endpoint", "token")


def test_copy_document(mocker):

    def mock_make_dys_request(self, method: str, url: str, headers=None, **kwargs):
        if "en_US" in headers.values():
            return {"status_code": 200, "text": "Copy of document.html"}
        elif "tr_TR" in headers.values():
            return {"status_code": 200, "text": "document.html - Kopya"}

    mocker.patch(
        'dys_connector.dys_api_manager.DYSManager.make_dys_request',
        mock_make_dys_request
    )

    res = manager.copy_document("cid", "parent", "en_US")
    assert res["status_code"] == 200
    assert res["text"] == "Copy of document.html"

    res = manager.copy_document("cid", "parent", "tr_TR")
    assert res["status_code"] == 200
    assert res["text"] == "document.html - Kopya"
