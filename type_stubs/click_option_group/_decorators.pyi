from typing import (
    Any,
    Callable,
    Optional,
    Type,
    TypeVar,
)

from ._core import OptionGroup as OptionGroup

F = TypeVar("F", bound=Callable[..., Any])

class _OptGroup:
    def __init__(self) -> None: ...
    def __call__(
        self,
        name: Optional[str] = ...,
        *,
        help: Optional[str] = ...,
        cls: Optional[Type[OptionGroup]] = ...,
        **attrs: Optional[Any],
    ) -> Callable[[F], F]: ...
    def group(
        self,
        name: Optional[str] = ...,
        *,
        help: Optional[str] = ...,
        cls: Optional[Type[OptionGroup]] = ...,
        **attrs: Optional[Any],
    ) -> Callable[[F], F]: ...
    def option(self, *param_decls: Optional[Any], **attrs: Optional[Any]) -> Callable[[F], F]: ...

optgroup: _OptGroup
