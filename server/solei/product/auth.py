from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, Organization, User
from solei.auth.scope import Scope

_CreatorProductsRead = Authenticator(
    required_scopes={
        Scope.web_read,
        Scope.web_write,
        Scope.products_read,
        Scope.products_write,
    },
    allowed_subjects={User, Organization},
)
CreatorProductsRead = Annotated[
    AuthSubject[User | Organization], Depends(_CreatorProductsRead)
]

_CreatorProductsWrite = Authenticator(
    required_scopes={
        Scope.web_write,
        Scope.products_write,
    },
    allowed_subjects={User, Organization},
)
CreatorProductsWrite = Annotated[
    AuthSubject[User | Organization], Depends(_CreatorProductsWrite)
]
