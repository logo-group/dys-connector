import json
from enum import Enum
from typing import Optional
from pydantic import BaseModel

# DYS "Kisisel Belge Turu" never changes
KISISEL_BELGE = "6a5547d5-09c1-4e18-816f-58fbaf1975bb"


class SharingRole(Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    COLLEAGUE = "COLLEAGUE"
    CONSUMER = "CONSUMER"


class VerificationType(Enum):
    NONE = 0, "verification.none",
    EMAIL_OTP = 1, "verification.via.email",
    SMS_OTP = 3, "verification.via.sms",
    IDM = 4, "verification.via.logo.idm";


class VarValues(BaseModel):
    """
    Abstract VarValues extend this class to define your own VarValues.
    """
    pass


class UploadDocumentDTO:
    def __init__(self, name, tag_ids=None, var_values: VarValues = VarValues().dict()):
        if tag_ids is None:
            tag_ids = KISISEL_BELGE
        self.name = name
        self.tagIds = [tag_ids]
        self.varValues = var_values.dict()
        for key in self.varValues.copy():
            if not self.varValues[key]:
                del self.varValues[key]

    def get_as_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


class SharingDTO(BaseModel):
    recipientId: Optional[str] = ""
    role: Optional[str] = SharingRole.CONSUMER.value
