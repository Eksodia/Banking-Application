from pydantic import BaseModel, ConfigDict

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserOut(BaseModel):
    id: str
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)
