from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, Organization, User
from solei.auth.scope import Scope

_OrdersRead = Authenticator(
    required_scopes={Scope.web_read, Scope.web_write, Scope.orders_read},
    allowed_subjects={User, Organization},
)
OrdersRead = Annotated[AuthSubject[User | Organization], Depends(_OrdersRead)]

_OrdersWrite = Authenticator(
    required_scopes={
        Scope.web_write,
        Scope.orders_write,
    },
    allowed_subjects={User, Organization},
)
OrdersWrite = Annotated[AuthSubject[User | Organization], Depends(_OrdersWrite)]
