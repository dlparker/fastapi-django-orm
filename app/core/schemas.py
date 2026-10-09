from pydantic import BaseModel, ConfigDict, Field


class UserIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class UserOut(BaseModel):
    # from_attributes lets FastAPI build this from a Django model instance
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
