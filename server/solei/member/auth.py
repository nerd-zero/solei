from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, User
from solei.auth.scope import Scope
from solei.models.organization import Organization

_MemberRead = Authenticator(
    required_scopes={
        Scope.web_read,
        Scope.web_write,
        Scope.members_read,
        Scope.members_write,
    },
    allowed_subjects={User, Organization},
)
MemberRead = Annotated[AuthSubject[User | Organization], Depends(_MemberRead)]

_MemberWrite = Authenticator(
    required_scopes={
        Scope.web_write,
        Scope.members_write,
    },
    allowed_subjects={User, Organization},
)
MemberWrite = Annotated[AuthSubject[User | Organization], Depends(_MemberWrite)]
