from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, User
from solei.auth.scope import Scope

_UserWrite = Authenticator(
    required_scopes={
        Scope.web_write,
        Scope.user_write,
    },
    allowed_subjects={User},
)
UserWrite = Annotated[AuthSubject[User], Depends(_UserWrite)]
