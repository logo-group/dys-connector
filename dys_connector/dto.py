import json
from pydantic import BaseModel

# DYS "Kisisel Belge Turu" never changes
KISISEL_BELGE = "6a5547d5-09c1-4e18-816f-58fbaf1975bb"


class VarValues(BaseModel):
    """
    Abstract VarValues extend this class to define your own VarValues.
    """
    pass


class UploadDocumentDTO:
    def __init__(self, name, tag_ids=None, var_values: VarValues = VarValues()):
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