from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import Anonymous, AuthSubject, User
from solei.auth.scope import Scope
from solei.models.organization import Organization

_CheckoutRead = Authenticator(
    required_scopes={
        Scope.web_read,
        Scope.web_write,
        Scope.checkouts_read,
        Scope.checkouts_write,
    },
    allowed_subjects={User, Organization},
)
CheckoutRead = Annotated[AuthSubject[User | Organization], Depends(_CheckoutRead)]

_CheckoutWrite = Authenticator(
    required_scopes={Scope.checkouts_write},
    allowed_subjects={User, Organization},
)
CheckoutWrite = Annotated[AuthSubject[User | Organization], Depends(_CheckoutWrite)]

_CheckoutWeb = Authenticator(
    required_scopes={Scope.web_write},
    allowed_subjects={User, Anonymous},
)
CheckoutWeb = Annotated[AuthSubject[User | Anonymous], Depends(_CheckoutWeb)]
