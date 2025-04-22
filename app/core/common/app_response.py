from typing import Generic, Optional, TypeVar
from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class AppBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(to_camel),
        populate_by_name=True
    )
    
    def model_dump(self, **kwargs):
        if "by_alias" not in kwargs:
            kwargs["by_alias"] = True
            
        return super().model_dump(**kwargs)


class AppResponse(AppBaseModel, Generic[T]):
    success: bool = Field(description="Is operation success", default=True)
    status_code: int = Field(description="status code", default=200)
    message: str = Field(description="Message back to client", default="done")
    data: Optional[T] = None

class WsAppResponse(AppBaseModel):
    error: str = Field(description="Ws error response", default=None)
    
    