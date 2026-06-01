from dataclasses import dataclass


@dataclass
class TenantContext:
    org_id: str
    workspace_id: str = "default"
    dataset: str = "default"

    @property
    def namespace(self):
        return f"{self.org_id}/{self.workspace_id}/{self.dataset}"
