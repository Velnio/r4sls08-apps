"""Immutable product identities for the shared transactional runtime."""

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class Product:
    id: str
    domain: str
    state_dir: str
    payload_path: str
    release_path: str
    status_prefix: str


PRODUCTS = MappingProxyType(
    {
        "r4sls08": Product(
            "r4sls08",
            "r4sls08",
            ".r4sls08-installer",
            "/opt/r4sls08/payload/r4sls08",
            "/opt/r4sls08/release.json",
            "R4SLS08_INSTALLER",
        ),
        "velnio": Product(
            "velnio",
            "velnio",
            ".velnio-installer",
            "/opt/r4sls08/payload/velnio",
            "/opt/r4sls08/release-velnio.json",
            "VELNIO_INSTALLER",
        ),
    }
)


def get_product(value="r4sls08"):
    if isinstance(value, Product):
        selected = PRODUCTS.get(value.id)
        if selected is not None and selected == value:
            return selected
    elif isinstance(value, str) and value in PRODUCTS:
        return PRODUCTS[value]
    raise ValueError("Unknown installer product")
