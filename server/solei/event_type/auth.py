from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, User
from solei.auth.scope import Scope
from solei.models.organization import Organization

_EventTypeRead = Authenticator(
    required_scopes={
        Scope.web_read,
        Scope.web_write,
        Scope.events_read,
        Scope.events_write,
    },
    allowed_subjects={User, Organization},
)
EventTypeRead = Annotated[AuthSubject[User | Organization], Depends(_EventTypeRead)]

_EventTypeWrite = Authenticator(
    required_scopes={
        Scope.web_write,
    },
    allowed_subjects={User, Organization},
)
EventTypeWrite = Annotated[AuthSubject[User | Organization], Depends(_EventTypeWrite)]
