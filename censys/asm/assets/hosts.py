"""Interact with the Censys Host Assets API."""
from .assets import Assets


class HostsAssets(Assets):
    """Hosts Assets API class."""

    def __init__(self, *args, **kwargs):
        """Inits HostsAssets."""
        super().__init__("hosts", *args, **kwargs)
