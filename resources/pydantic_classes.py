from enum import Enum

from pydantic import BaseModel, Field, field_validator

class States(str, Enum):
    armor = "Armor"
    health = "Health"
    health_regen = "Health Regen"
    magic_resist = "Magic Resist"
    omni_vamp = "Omni Vamp"