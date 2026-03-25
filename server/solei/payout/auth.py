from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, User
from solei.auth.scope import Scope

_PayoutsRead = Authenticator(
    required_scopes={
        Scope.web_read,
        Scope.web_write,
        Scope.payouts_read,
    },
    allowed_subjects={User},
)
PayoutsRead = Annotated[AuthSubject[User], Depends(_PayoutsRead)]

_PayoutsWrite = Authenticator(
    required_scopes={
        Scope.web_write,
        Scope.payouts_write,
    },
    allowed_subjects={User},
)
PayoutsWrite = Annotated[AuthSubject[User], Depends(_PayoutsWrite)]
