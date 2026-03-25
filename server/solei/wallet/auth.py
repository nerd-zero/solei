from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, Organization, User
from solei.auth.scope import Scope

_WalletsRead = Authenticator(
    required_scopes={Scope.web_read, Scope.web_write, Scope.wallets_read},
    allowed_subjects={User, Organization},
)
WalletsRead = Annotated[AuthSubject[User | Organization], Depends(_WalletsRead)]

_WalletsWrite = Authenticator(
    required_scopes={
        Scope.web_write,
        Scope.wallets_write,
    },
    allowed_subjects={User, Organization},
)
WalletsWrite = Annotated[AuthSubject[User | Organization], Depends(_WalletsWrite)]
