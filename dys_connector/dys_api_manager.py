import requests
import json
from enum import Enum

# Used endpoints of DYS
ENDPOINTS = {
    "COPY": "/api/v2.0/document/copy/{}",
    "RENAME": "/api/v2.0/document/rename/{}",
    "UPLOAD": "/api/v2.0/document/uploadDocument",
    "STATE": "/api/diagnose",
    "DIR_STRUCTURE": "/api/v2.0/document/directoryStructure",
    "GET_DOC_META": "/api/v2.0/document/viewDocumentMetadata/{}",
    "UPDATE_DOC_META": "/api/v2.0/document/updateMetadata/{}",
    "GET_DOC_INFO": "/api/v2.0/document/getDocumentWithoutContent/{}",
    "EXTERNAL_SHARE": "/api/v2.0/document/externalShare/{}",
    "DOC_CONTENT": "/api/v2.0/document/content/{}"
}


class Container(Enum):
    """
    Container Type Enum
    """
    DIRECTORY = "DIRECTORY"
    SPACE = "SPACE"
    BPM = "BPM"
    SHARED = "SHARED"
    DOCUMENT = "DOCUMENT"
    TRASH = "TRASH"
    SHARE_INNER = "SHARE_INNER"
    SEARCH_EVERYWHERE = "SEARCH_EVERYWHERE"
    SHARED_BY_ME = "SHARED_BY_ME"
    SPACE_SHARE_INNER = "SPACE_SHARE_INNER"


class DYSManager:
    """
    A class to interact with Logo DYS(Doküman Yönetim Sitemi) API

    Attributes
    ----------
    dys_base_url : str
        Dys Endpoint e.g.: "https://dys.logo.cloud"
    TOKEN: str
        Logo IDM token for Authentication & Authorization
    """

    def __init__(self, dys_base_url, idm_token):
        if None in (dys_base_url, idm_token):
            raise ValueError("DYS Base Url or IDM Token cannot be None!")
        if dys_base_url[-1] == '/':
            dys_base_url = dys_base_url[:-1]
        self.dys_base_url = dys_base_url
        self.TOKEN = idm_token
        self.HEADERS = {
            "Authorization": "Bearer " + self.TOKEN,
        }

    def get_url(self, task):
        """
        :param task: task name
        :return: string. Returns the endpoint for a specific task
        :exception: KeyError if task not exist
        """
        return self.dys_base_url + ENDPOINTS[task]

    def check_state(self):
        """
        Check for DYS Application State
        :return: state
            Possible values for global “state”
                FINE: All diagnose methods ended with success.
                WARNING: A non-mandatory diagnose method FAILed.
                FAILURE:  A mandatory diagnose method FAILed.
            If request is not successful, returns response text.
        """
        url = self.get_url("STATE")
        res = self.make_dys_request("GET", url=url, headers={})
        if res.status_code not in [200, 202]:
            return res.text
        status_dict = json.loads(res.text)
        if "state" in status_dict.keys():
            return status_dict["state"]
        return res

    def make_dys_request(self, method: str, url: str, headers=None, **kwargs):
        """
        General DYS requests with basic error handling
        :param method: Request method. Ex: "GET", "POST", "PUT"
        :param url: Request url
        :param headers: (optional) Request headers
        :param kwargs: (optional) Optional parameters of request method. Ex: data, files etc.
        :return: :class:`Response <Response>` object
        """
        if not headers:
            headers = self.HEADERS
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            return response
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("RequestException:", err)

        return None

    def post_content(self, parent_folder_cid, payload, files):
        """
        :param parent_folder_cid: Parent folder cid that document will be uploaded
        :param payload:
        :param files:
        :return: :class:`Response <Response>` object
        """
        url = self.get_url("UPLOAD") + "?parentFolderCid=" + parent_folder_cid
        response = self.make_dys_request("POST", url, data=payload, files=files)
        return response

    def get_dir_structure(self, folder_cid: str, _from: int = 0, _to: int = 10000, cont_type: Container = Container.SPACE):
        """
        Get content list of a directory.
        :param folder_cid: Directory Cid
        :param _from: (default:0) Ignore files till from parameter
        :param _to: (default:10000) File limit. DYS supports maximum 10000 for structure request.
        :param cont_type: Container type defaults to SPACE
        :return: List of Dicts. Each dict refers the basic information of a document.
        """
        url = self.get_url("DIR_STRUCTURE") + '?folderCid={}&from={}&size={}&containerType={}'.format(folder_cid, _from, _to, cont_type.name)
        headers = self.HEADERS
        headers["Content-Type"] = "application/json"
        res = self.make_dys_request("GET", url, headers=headers)
        dir_list = json.loads(res.text)
        return dir_list

    def get_doc_metadata(self, doc_cid):
        """
        Get Metadata of a Document
        :param doc_cid: Document Cid
        :return:
        """
        url = self.get_url("GET_DOC_META").format(doc_cid)
        headers = self.HEADERS
        headers["Content-Type"] = "application/json"
        res = json.loads(self.make_dys_request("GET", url, headers=headers).text)
        metadata = res["varValues"]
        return metadata

    def update_metadata(self, doc_cid: str, metadata: dict, doc_type_id: str):
        """
        Update a document metadata
        :param doc_cid: Document Cid
        :param metadata: New metadata dict of the document
        :param doc_type_id: Document type id that refers to metadata group.
        :return: Updated document Cid
        """
        url = self.get_url("UPDATE_DOC_META").format(doc_cid)
        pay_dict = {"documentTypeIds": [], "tagIds": [doc_type_id], "varValues": metadata}
        payload = json.dumps(pay_dict).encode("utf-8")
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": "Bearer " + self.TOKEN,
        }
        res = self.make_dys_request("PUT", url, headers=headers, data=payload)
        # print(res.status_code, res.text)
        return res

    def get_document_without_content(self, doc_cid):
        """
        Get document information and details from DYS. (Not Document Content!)
        :param doc_cid: Document Cid
        :return: dict: Document details
        """
        url = self.get_url("GET_DOC_INFO").format(doc_cid)
        headers = self.HEADERS
        headers["Content-Type"] = "application/json"
        res = self.make_dys_request("GET", url, headers=headers)
        document = json.loads(res.text)
        return document

    def generate_external_share(self, doc_cid, hide_name: bool = True, doc_name: str = "string", dur_day: int = 0,
                                email_list: list = ["string"], idm_ex_share: bool = True, ignore_kafka: bool = True):
        """
        Generate external share url for a document.
        :param doc_cid: Document Cid
        :param hide_name: bool: Hide document name on external share.
        :param doc_name: id for external share
        :param dur_day: External share duration as day, default 0 refers to limitless.
        :param email_list: Shared users' emails
        :param idm_ex_share: IDM External Share defaults to True
        :param ignore_kafka: Ignore Kafka settings defaults to True
        :return: External share url string
        """
        url = self.get_url("EXTERNAL_SHARE").format(doc_cid)
        headers = self.HEADERS
        headers["Content-Type"] = "application/json;charset=UTF-8"

        payload = {"documentName": doc_name, "durationDay": dur_day, "emailList": email_list,
                   "idmExternalShare": str(idm_ex_share).lower(), "ignoreKafka": str(ignore_kafka).lower()}
        payload = json.dumps(payload)
        response = requests.request("POST", url, headers=headers, data=payload)
        value = json.loads(response.text)
        external_url = value["externalShareMailLinkMap"]["string"] + "&hideName={}".format(hide_name)
        return external_url

    def get_document_content(self, doc_cid):
        """
        Get content of a document from DYS.
        :param doc_cid: Document Cid
        :return: str: Document content
        """
        url = self.get_url("DOC_CONTENT").format(doc_cid)
        headers = self.HEADERS
        headers["Content-Type"] = "application/json"
        response = self.make_dys_request("GET", url, headers=headers)
        value = response.text
        return value

    def copy_document(self, doc_cid, parent_folder_cid=None):
        """
        Copy a document to the root or a specified location
        :param doc_cid: Document Cid
        :param parent_folder_cid: (Optional) Target folder Cid that document will be copied. If none, target is root.
        :return: Cid of the new document.
        """
        url = end_point = self.get_url("COPY").format(doc_cid)
        if parent_folder_cid:
            url = end_point + "?targetFolderCid=" + parent_folder_cid
        res = self.make_dys_request("POST", url)
        return res

    def rename_document(self, doc_cid, name):
        """
        Rename a document
        :param doc_cid: Document Cid
        :param name: New name of the document
        :return: Cid of the renamed document
        """
        end_point = self.get_url("RENAME").format(doc_cid)
        url = end_point + "?fileName=" + name
        res = self.make_dys_request("POST", url)
        return res
