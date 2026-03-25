from typing import Annotated

from fastapi import Depends

from solei.auth.dependencies import Authenticator
from solei.auth.models import Anonymous, AuthSubject, Organization, User
from solei.auth.scope import Scope

OrganizationsRead = Annotated[
    AuthSubject[User | Organization],
    Depends(
        Authenticator(
            required_scopes={
                Scope.web_read,
                Scope.web_write,
                Scope.organizations_read,
                Scope.organizations_write,
            },
            allowed_subjects={User, Organization},
        )
    ),
]

OrganizationsWrite = Annotated[
    AuthSubject[User | Organization],
    Depends(
        Authenticator(
            required_scopes={
                Scope.web_write,
                Scope.organizations_write,
            },
            allowed_subjects={User, Organization},
        )
    ),
]

OrganizationsCreate = Annotated[
    AuthSubject[User],
    Depends(
        Authenticator(
            required_scopes={
                Scope.web_write,
                Scope.organizations_write,
            },
            allowed_subjects={User},
        )
    ),
]

OrganizationsWriteUser = Annotated[
    AuthSubject[User],
    Depends(
        Authenticator(
            required_scopes={
                Scope.web_write,
                Scope.organizations_write,
            },
            allowed_subjects={User},
        )
    ),
]

OrganizationsReadOrAnonymous = Annotated[
    AuthSubject[User | Organization | Anonymous],
    Depends(
        Authenticator(
            required_scopes=set(),  # No required scopes for this authenticator
            allowed_subjects={User, Organization, Anonymous},
        )
    ),
]
