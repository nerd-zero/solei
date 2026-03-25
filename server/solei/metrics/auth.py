from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, Organization, User
from solei.auth.scope import Scope

_MetricsRead = Authenticator(
    required_scopes={Scope.web_read, Scope.web_write, Scope.metrics_read},
    allowed_subjects={User, Organization},
)
MetricsRead = Annotated[AuthSubject[User | Organization], Depends(_MetricsRead)]
