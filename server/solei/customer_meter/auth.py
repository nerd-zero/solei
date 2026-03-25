from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, User
from solei.auth.scope import Scope
from solei.models.organization import Organization

_CustomerMeterRead = Authenticator(
    required_scopes={
        Scope.web_read,
        Scope.web_write,
        Scope.customer_meters_read,
    },
    allowed_subjects={User, Organization},
)
CustomerMeterRead = Annotated[
    AuthSubject[User | Organization], Depends(_CustomerMeterRead)
]
