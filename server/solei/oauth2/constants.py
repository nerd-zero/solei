from solei.config import settings

from .sub_type import SubType

CLIENT_ID_PREFIX = "solei_ci_"
CLIENT_SECRET_PREFIX = "solei_cs_"
CLIENT_REGISTRATION_TOKEN_PREFIX = "solei_crt_"
AUTHORIZATION_CODE_PREFIX = "solei_ac_"
ACCESS_TOKEN_PREFIX: dict[SubType, str] = {
    SubType.user: "solei_at_u_",
    SubType.organization: "solei_at_o_",
}
REFRESH_TOKEN_PREFIX: dict[SubType, str] = {
    SubType.user: "solei_rt_u_",
    SubType.organization: "solei_rt_o_",
}
WEBHOOK_SECRET_PREFIX = "solei_whs_"

ISSUER = "https://solei.to"
SERVICE_DOCUMENTATION = "https://solei.to/docs"
SUBJECT_TYPES_SUPPORTED = ["public"]
ID_TOKEN_SIGNING_ALG_VALUES_SUPPORTED = ["RS256"]
CLAIMS_SUPPORTED = ["sub", "name", "email", "email_verified"]

JWT_CONFIG = {
    "key": settings.JWKS.find_by_kid(settings.CURRENT_JWK_KID),
    "alg": "RS256",
    "iss": ISSUER,
    "exp": 3600,
}


def is_registration_token_prefix(value: str) -> bool:
    return value.startswith(CLIENT_REGISTRATION_TOKEN_PREFIX)
