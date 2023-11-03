import json
import logging
import requests
import dys_connector.exceptions as dys_exc

from enum import Enum
from dys_connector.dto import VerificationType

DEFAULT_HEADER = "application/json"

# Used endpoints of DYS
ENDPOINTS = {
    "COPY": "/api/v2.0/document/copy/{cid}",
    "RENAME": "/api/v2.0/document/rename/{cid}",
    "UPLOAD_DOCUMENT": "/api/v2.0/document/uploadDocument",
    "UPLOAD_FOLDER": "/api/v2.0/document/uploadFolder",
    "STATE": "/api/diagnose",
    "DIR_STRUCTURE": "/api/v2.0/document/directoryStructure",
    "GET_DOC_META": "/api/v2.0/document/viewDocumentMetadata/{cid}",
    "UPDATE_DOC_META": "/api/v2.0/document/updateMetadata/{cid}",
    "GET_DOC_INFO": "/api/v2.0/document/getDocumentWithoutContent/{cid}",
    "EXTERNAL_SHARE": "/api/v2.0/document/externalShare/{cid}",
    "DOC_CONTENT": "/api/v2.0/document/content/{cid}",
    "DELETE": "/api/v2.0/document/delete/{cid}",
    "DELETE_PERMA": "/api/v2.0/document/deletePermanently/{cid}"
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

    def __init__(self, dys_base_url, idm_token, corid=None):
        if None in (dys_base_url, idm_token):
            raise ValueError("DYS Base Url or IDM Token cannot be None!")
        if dys_base_url[-1] == '/':
            dys_base_url = dys_base_url[:-1]
        self.dys_base_url = dys_base_url
        self.TOKEN = idm_token
        self.HEADERS = {
            "Authorization": "Bearer " + self.TOKEN,
        }
        self.corid = corid

    def get_url(self, task: str):
        """
        Generates the domain appropriate url
        :param task: task name
        :return: string. Returns the endpoint for a specific task
        :exception: KeyError if task not exist
        """
        return self.dys_base_url + ENDPOINTS[task]

    @staticmethod
    def check_dys_exception(response: requests.Response):
        code = response.status_code

        if int(code / 100) == 2:
            logging.debug({'status_code': code, 'dys_response': response.text})
        else:
            logging.error({'status_code': code, 'dys_response': response.text})

        if code == 400:
            raise dys_exc.DysBadRequestError()
        elif code == 401:
            raise dys_exc.DysUnauthorizedError()
        elif code == 500:
            raise dys_exc.DysInternalServerError()
        elif code == 502:
            raise dys_exc.DysBadGatewayError()
        elif code == 503:
            raise dys_exc.DysServiceTemporarilyUnavailable()
        elif int(code / 100) != 2:
            raise dys_exc.DysHttpException(status_code=code)

    def make_dys_request(self, method: str, url: str, headers=None, **kwargs):
        """
        General DYS requests with basic error handling
        :param method: Request method. Ex: "GET", "POST", "PUT"
        :param url: Request url
        :param headers: (optional) Request headers
        :param kwargs: (optional) Optional parameters of request method. Ex: data, files etc.
        :return: :class:`Response <Response>` object
        """
        log = {**{'method': method, 'url': url}, **kwargs}
        if not headers:
            headers = self.HEADERS.copy()
        if self.corid:
            headers.update({'corid': self.corid})
            log.update({'corid': self.corid})

        logging.info(log)

        response = requests.request(method, url, headers=headers, **kwargs)
        self.check_dys_exception(response)
        return response

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

    def post_folder(self, parent_folder_cid: str, folder_name: str):
        """
        Upload folders to DYS
        :param parent_folder_cid: Parent folder cid that document will be uploaded
        :param folder_name: Parent folder name of folders in folders list
        :return: New folder's cid
        """
        url = self.get_url("UPLOAD_FOLDER") + "?parentFolderCid=" + parent_folder_cid + "&folderName=" + folder_name
        headers = self.HEADERS.copy()
        headers["Content-Type"] = f"{DEFAULT_HEADER};charset=UTF-8"
        response = self.make_dys_request("POST", url, headers=headers)
        value_parent = json.loads(response.text)
        return value_parent["cid"]

    def post_content(self, parent_folder_cid: str, payload: dict, files: list):
        """
        Uploads document to DYS
        :param parent_folder_cid: Parent folder cid that document will be uploaded
        :param payload: A dict that contains "uploadDocumentDTO". Ex: {"uploadDocumentDTO": ''}
        :param files: File list. Ex: [("file", (doc["filename"], doc["file"], "text/html"))]
        :return: :class:`Response <Response>` object
        """
        url = self.get_url("UPLOAD_DOCUMENT") + "?parentFolderCid=" + parent_folder_cid
        headers = self.HEADERS.copy()
        headers["Content-Type"] = "multipart/form-data"
        response = self.make_dys_request("POST", url, data=payload, files=files)
        return response

    def get_dir_structure(self, folder_cid: str, _from: int = 0, _to: int = 10000,
                          cont_type: Container = Container.SPACE):
        """
        Get content list of a directory.
        :param folder_cid: Directory Cid
        :param _from: (default:0) Ignore files till from parameter
        :param _to: (default:10000) File limit. DYS supports maximum 10000 for structure request.
        :param cont_type: Container type defaults to SPACE
        :return: List of Dicts. Each dict refers the basic information of a document.
        """
        url = self.get_url(
            "DIR_STRUCTURE") + f'?folderCid={folder_cid}&from={_from}&size={_to}&containerType={cont_type.name} '
        headers = self.HEADERS.copy()
        headers["Content-Type"] = DEFAULT_HEADER
        res = self.make_dys_request("GET", url, headers=headers)
        dir_list = json.loads(res.text)
        return dir_list

    def get_doc_metadata(self, doc_cid: str):
        """
        Get Metadata of a Document
        :param doc_cid: Document Cid
        :return: Returns a dict that contains document metadata
        """
        url = self.get_url("GET_DOC_META").format(cid=doc_cid)
        headers = self.HEADERS.copy()
        headers["Content-Type"] = DEFAULT_HEADER
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
        url = self.get_url("UPDATE_DOC_META").format(cid=doc_cid)
        pay_dict = {"documentTypeIds": [], "tagIds": [doc_type_id], "varValues": metadata}
        payload = json.dumps(pay_dict).encode("utf-8")
        headers = {
            "Content-Type": f"{DEFAULT_HEADER};charset=UTF-8",
            "Authorization": "Bearer " + self.TOKEN,
        }
        res = self.make_dys_request("PUT", url, headers=headers, data=payload)
        return res

    def get_document_without_content(self, doc_cid: str):
        """
        Get document information and details from DYS. (Not Document Content!)
        :param doc_cid: Document Cid
        :return: dict: Document details
        """
        url = self.get_url("GET_DOC_INFO").format(cid=doc_cid)
        headers = self.HEADERS.copy()
        headers["Content-Type"] = DEFAULT_HEADER
        res = self.make_dys_request("GET", url, headers=headers)
        document = json.loads(res.text)
        return document

    def get_external_share(self, doc_cid: str, hide_name: bool = True) -> list:
        """
        Get existing external share url for a document.
        :param doc_cid: Document Cid
        :param hide_name: bool: Hide document name on external share.
        :return: External share url string
        """
        url = self.get_url("EXTERNAL_SHARE").format(cid=doc_cid)
        headers = self.HEADERS.copy()
        headers["Content-Type"] = f"{DEFAULT_HEADER};charset=UTF-8"
        response = self.make_dys_request("GET", url, headers=headers)
        value = json.loads(response.text)
        return list(map(lambda link: link + "&hideName={}".format(hide_name), (item['shareLink'] for item in value)))

    def generate_external_share(self, doc_cid: str, hide_name: bool = True,
                                role_id_list: list = [],
                                disposable: bool = False,
                                download_disabled: bool = False,
                                verification_type = VerificationType.NONE
                                ):
        """
        Generate external share url for a document.
        :param doc_cid: Document Cid
        :param hide_name: bool: Hide document name on external share.
        :param role_id_list:
        :param disposable:
        :param download_disabled:
        :param verification_type:
        :return: External share url string
        """
        url = self.get_url("EXTERNAL_SHARE").format(cid=doc_cid)
        headers = self.HEADERS.copy()
        headers["Content-Type"] = f"{DEFAULT_HEADER};charset=UTF-8"
        payload = {
            "authorizationRoleList": role_id_list,
            "cancelled": "false",
            "disposable": str(disposable).lower(),
            "downloadDisabled": str(download_disabled).lower(),
            "ignoreKafka": "true",
            "passwordProtected": "false",
            "uploadEnabled": "false",
            "verificationType": verification_type.value[0]
        }
        if len(role_id_list) == 0:
            del payload['authorizationRoleList']
        if verification_type is VerificationType.IDM:
            payload.update({"idmExternalShare": "true"})
        payload = json.dumps(payload)
        response = self.make_dys_request("POST", url, headers=headers, data=payload)
        value = json.loads(response.text)
        external_url = value["externalShareMailLinkMap"][
                           next(iter(value["externalShareMailLinkMap"]))] + "&hideName={}".format(hide_name)
        return external_url

    def get_document_content(self, doc_cid: str) -> str:
        """
        Get content of a document from DYS.
        :param doc_cid: Document Cid
        :return: str: Document content
        """
        url = self.get_url("DOC_CONTENT").format(cid=doc_cid)
        headers = self.HEADERS.copy()
        headers["Content-Type"] = DEFAULT_HEADER
        response = self.make_dys_request("GET", url, headers=headers)
        value = response.text
        return value

    def copy_document(self, doc_cid: str, parent_folder_cid: str = None, x_lang: str = None,
                      add_copy_of_prefix: bool = False):
        """
        Copy a document to the root or a specified location
        :param doc_cid: Document Cid
        :param parent_folder_cid: (Optional) Target folder Cid that document will be copied. If none, target is root.
        :param add_copy_of_prefix: (Optional) Determines if name prefix (Copy-of) added to copied items.
        :param x_lang: (Optional) Copy Language Parameter. Ex: tr_TR or en_US. This decides if new document name
        comes with Copy of or - Kopya
        :return: Cid of the new document.
        """
        url = self.get_url("COPY").format(cid=doc_cid)
        headers = self.HEADERS.copy()
        headers["Content-Type"] = DEFAULT_HEADER
        if x_lang:
            headers["X-Lang"] = x_lang
        params = {"addCopyOfPrefix": add_copy_of_prefix}
        if parent_folder_cid:
            params.update({"targetFolderCid": parent_folder_cid})
        res = self.make_dys_request("POST", url, headers, params=params)
        return res

    def rename_document(self, doc_cid: str, name: str):
        """
        Rename a document
        :param doc_cid: Document Cid
        :param name: New name of the document
        :return: Cid of the renamed document
        """
        end_point = self.get_url("RENAME").format(cid=doc_cid)
        url = end_point + "?fileName=" + name
        res = self.make_dys_request("POST", url)
        return res

    def delete(self, cid: str) -> requests.Response:
        """
        Delete and send a document or folder to recycle.
        :param cid: Dys Cid
        :return: Request Response
        """
        url = self.get_url("DELETE").format(cid=cid)
        res = self.make_dys_request(method="DELETE", url=url)
        return res

    def delete_permanently(self, cid: str) -> requests.Response:
        """
        Delete a document or folder permanently.
        :param cid: Dys Cid
        :return: Request Response
        """
        url = self.get_url("DELETE_PERMA").format(cid=cid)
        res = self.make_dys_request(method="DELETE", url=url)
        return res

    def clear_directory(self, cid: str) -> str:
        """
        Delete all files and subfolders inside a directory.
        :param cid: Dys Cid
        :return: Cid of folder
        """
        dir_list = self.get_dir_structure(folder_cid=cid, cont_type=Container.DIRECTORY)
        for item in dir_list:
            try:
                self.delete(item["cid"])
            except Exception:
                raise dys_exc.DysClearDirectoryItemDeleteException()
        return cid
