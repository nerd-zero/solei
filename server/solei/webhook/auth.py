from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, Organization, User
from solei.auth.scope import Scope

_WebhooksRead = Authenticator(
    required_scopes={
        Scope.web_read,
        Scope.web_write,
        Scope.webhooks_read,
        Scope.webhooks_write,
    },
    allowed_subjects={User, Organization},
)
WebhooksRead = Annotated[AuthSubject[User | Organization], Depends(_WebhooksRead)]

_WebhooksWrite = Authenticator(
    required_scopes={
        Scope.web_write,
        Scope.webhooks_write,
    },
    allowed_subjects={User, Organization},
)
WebhooksWrite = Annotated[AuthSubject[User | Organization], Depends(_WebhooksWrite)]
