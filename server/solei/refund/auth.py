from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, Organization, User
from solei.auth.scope import Scope

RefundsRead = Annotated[
    AuthSubject[User | Organization],
    Depends(
        Authenticator(
            required_scopes={
                Scope.web_read,
                Scope.web_write,
                Scope.refunds_read,
                Scope.refunds_write,
            },
            allowed_subjects={User, Organization},
        )
    ),
]

RefundsWrite = Annotated[
    AuthSubject[User | Organization],
    Depends(
        Authenticator(
            required_scopes={
                Scope.web_write,
                Scope.refunds_write,
            },
            allowed_subjects={User, Organization},
        )
    ),
]
