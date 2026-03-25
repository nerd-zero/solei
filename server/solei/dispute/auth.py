from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, Organization, User
from solei.auth.scope import Scope

_DisputesRead = Authenticator(
    required_scopes={Scope.web_read, Scope.web_write, Scope.disputes_read},
    allowed_subjects={User, Organization},
)
DisputesRead = Annotated[AuthSubject[User | Organization], Depends(_DisputesRead)]
