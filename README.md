# dys-connector
Logo DYS (Doküman Yönetim Sitemi) API Python Implementation

#### Quick Start

```
from dys_connector.dys_api_manager import DYSManager
import json

idm_token = "XXXXXXXXXXXXXXXXXXXXXX"
dys_base_url = "https://DYS_BASE_URL"

manager = DYSManager(dys_base_url, TOKEN)

# Check state of DYS. FINE-WARNING-FAILURE
state = manager.check_state()

# Post Content to DYS
parent_folder_cid = "111111111111111111111"
doc_tag_id = "123123123123"
doc = {"file": open_file("testdoc1.html"), "filename": "testdoc1.html", "metadata": None}
f = [("file", (doc["filename"], doc["file"], "text/html"))]
dto = {
        "name": "testdoc1.html",
        "tagIds": [doc_type_id],
        "varValues": {"meta1": "value1", "meta2": "value2"},
        "documentTypeIds": []
       }
payload = {"uploadDocumentDTO": json.dumps(dto)}
res = manager.post_content(parent_folder_cid, payload, f)
print(res.text)

# Get and update document metadata
doc_cid = "abd123123123abc123123123"

meta = manager.get_doc_metadata(doc_cid)
external_url = manager.generate_external_share(doc_cid)
meta['doc_url'] = external_url
meta['dys_cid'] = cid
manager.update_metadata(cid,meta,doc_type_id_confluence)

# Copy and rename document
new_folder_cid = "123newfolder123123123"
res = manager.copy_document(doc_cid, new_folder_cid)
res2 = manager.rename_document(json.loads(res.text)["cid"], "new_doc_name")

```
