"""Every model, so ``metadata`` knows all tables (used by migrations and their tests)."""

from homestead_finance.core.db import Base
from homestead_finance.farm.models import Farm
from homestead_finance.spike.models import SpikeEntry

metadata = Base.metadata

__all__ = ["Farm", "SpikeEntry", "metadata"]
