from typing import Dict, List, Optional, TypedDict
import requests


class GrafanaOrganizationAddress(TypedDict):
    address1: str
    address2: str
    city: str
    zipCode: str
    state: str
    countrys: str


class GrafanaOrganization(TypedDict):
    id: int
    name: str
    address: Optional[GrafanaOrganizationAddress]


class GrafanaCreateOrganizationResponse(TypedDict):
    orgId: str
    message: str


class GrafanaDeleteOrganizationResponse(TypedDict):
    message: str


class GrafanaApi:
    def __init__(
        self,
        host: str = None,
        port: int = 3000,
        admin_username: str = "admin",
        admin_password: str = "admin",
        use_tls: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.user = admin_username
        self.password = admin_password
        self.use_tls = use_tls

    def _url(self, path):
        protocol = "https" if self.use_tls else "http"
        return f"{protocol}://{self.user}:{self.password}@{self.host}:{self.port}{path}"

    def _get(self, path):
        url = self._url(path)
        res = requests.get(
            url,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

        if res.status_code >= 300:
            raise Exception(
                f"Failed to GET request resource path {url} with status code: {res.status_code}"
            )

        return res.json()

    def _delete(self, path):
        url = self._url(path)
        res = requests.delete(
            url,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

        if res.status_code >= 300:
            raise Exception(
                f"Failed to GET request resource path {url} with status code: {res.status_code}"
            )

        return res.json()

    def _post(self, path, data: Dict):
        url = self._url(path)
        res = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=data,
        )

        if res.status_code >= 300:
            raise Exception(
                f"Failed to POST request resource path {url} with status code: {res.status_code}"
            )
        return res.json()

    def get_organizations(self) -> List[GrafanaOrganization]:
        return self._get("/api/orgs")

    def get_organization_by_name(self, org_name: str) -> GrafanaOrganization:
        return self._get(f"/api/orgs/name/{org_name}")

    def create_organization(self, org_name: str) -> GrafanaCreateOrganizationResponse:
        return self._post("/api/orgs", data={"name": org_name})

    def delete_organization(self, org_id: int) -> GrafanaDeleteOrganizationResponse:
        return self._delete(f"/api/orgs/{org_id}")
