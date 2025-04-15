from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# Prevent circular imports during runtime while allowing type checking during development
if TYPE_CHECKING:
    from .models import TaxonName

# Define the Taxon table
class Taxon(SQLModel, table=True):
    tax_id: int = Field(primary_key=True)  # Unique taxon identifier
    parent_tax_id: Optional[int] = Field(default=None, foreign_key="taxon.tax_id")  # Foreign key to parent
    rank: Optional[str]  # e.g., "species", "genus", etc.

    # Self-referential relationships
    parent: Optional["Taxon"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Taxon.tax_id"}
    )
    children: List["Taxon"] = Relationship(back_populates="parent")

    # One-to-many relationship with names
    names: List["TaxonName"] = Relationship(back_populates="taxon")

# Define the TaxonName table
class TaxonName(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tax_id: int = Field(foreign_key="taxon.tax_id")  # Link to Taxon
    name_txt: str  # Name string
    unique_name: Optional[str]  # Rarely used; can be left blank
    name_class: str  # e.g., "scientific name", "synonym", etc.

    # Link back to Taxon
    taxon: Optional[Taxon] = Relationship(back_populates="names")
