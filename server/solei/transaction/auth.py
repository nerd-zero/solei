from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import AuthSubject, User
from solei.auth.scope import Scope

_TransactionsRead = Authenticator(
    required_scopes={
        Scope.web_read,
        Scope.web_write,
        Scope.transactions_read,
    },
    allowed_subjects={User},
)
TransactionsRead = Annotated[AuthSubject[User], Depends(_TransactionsRead)]

_TransactionsWrite = Authenticator(
    required_scopes={
        Scope.web_write,
        Scope.transactions_write,
    },
    allowed_subjects={User},
)
TransactionsWrite = Annotated[AuthSubject[User], Depends(_TransactionsWrite)]
