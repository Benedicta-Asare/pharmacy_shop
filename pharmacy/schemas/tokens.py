from pydantic import BaseModel

class Token(BaseModel):
    token_type: str
    access_token: str