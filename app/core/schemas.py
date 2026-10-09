from pydantic import BaseModel, ConfigDict, Field


class ClientIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class ClientOut(BaseModel):
    # from_attributes lets FastAPI build this from a Django model instance
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
