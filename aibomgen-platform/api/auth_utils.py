from fastapi import Depends
from fastapi_azure_auth import MultiTenantAzureAuthorizationCodeBearer
from fastapi_azure_auth.user import User
import os

AUTH_ENABLED = os.getenv("AUTH_ENABLED", "true").lower() == "true"

if AUTH_ENABLED:
    azure_scheme = MultiTenantAzureAuthorizationCodeBearer(
        app_client_id=os.getenv("APP_CLIENT_ID"),
        scopes={
            f'api://{os.getenv("APP_CLIENT_ID")}/user_impersonation': 'user_impersonation',
        },
        validate_iss=False,
    )

    def get_current_user(user: User = Depends(azure_scheme)):
        return user
else:
    def get_current_user():
        class DummyUser:
            claims = {"oid": "anonymous"}
        return DummyUser()
