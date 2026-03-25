from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, User
from solei.auth.scope import Scope
from solei.models.organization import Organization

_PaymentRead = Authenticator(
    required_scopes={
        Scope.web_read,
        Scope.web_write,
        Scope.payments_read,
    },
    allowed_subjects={User, Organization},
)
PaymentRead = Annotated[AuthSubject[User | Organization], Depends(_PaymentRead)]
