from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OpenModelContainerInfo(_message.Message):
    __slots__ = ("name", "version", "author", "biography")
    class Author(_message.Message):
        __slots__ = ("name", "email")
        NAME_FIELD_NUMBER: _ClassVar[int]
        EMAIL_FIELD_NUMBER: _ClassVar[int]
        name: str
        email: str
        def __init__(self, name: _Optional[str] = ..., email: _Optional[str] = ...) -> None: ...
    class Biography(_message.Message):
        __slots__ = ("summary",)
        SUMMARY_FIELD_NUMBER: _ClassVar[int]
        summary: str
        def __init__(self, summary: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    BIOGRAPHY_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    author: OpenModelContainerInfo.Author
    biography: OpenModelContainerInfo.Biography
    def __init__(self, name: _Optional[str] = ..., version: _Optional[str] = ..., author: _Optional[_Union[OpenModelContainerInfo.Author, _Mapping]] = ..., biography: _Optional[_Union[OpenModelContainerInfo.Biography, _Mapping]] = ...) -> None: ...
