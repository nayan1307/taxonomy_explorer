from sqlmodel import Session
from app.models import Taxon, TaxonName
from app.database import engine, create_db_and_tables

# Function to parse small_nodes.dmp and load taxon records
def load_nodes(file_path: str):
    taxa = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]
            tax_id = int(parts[0])               # Unique identifier
            parent_tax_id = int(parts[1])        # Parent's tax_id
            rank = parts[2]                      # Taxonomic rank
            taxa.append(Taxon(tax_id=tax_id, parent_tax_id=parent_tax_id, rank=rank))
    return taxa

# Function to parse small_names.dmp and load name records
def load_names(file_path: str):
    names = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]
            tax_id = int(parts[0])                       # Foreign key to Taxon
            name_txt = parts[1]                          # Name value
            unique_name = parts[2] or None               # Usually empty
            name_class = parts[3]                        # e.g., scientific name, synonym
            names.append(TaxonName(
                tax_id=tax_id,
                name_txt=name_txt,
                unique_name=unique_name,
                name_class=name_class
            ))
    return names

# Main population function: creates tables, loads data, and commits to DB
def populate_database():
    create_db_and_tables()

    nodes = load_nodes("data/small_nodes.dmp")      # Load node data
    names = load_names("data/small_names.dmp")      # Load name data

    with Session(engine) as session:
        session.add_all(nodes)                      # Add Taxon objects
        session.add_all(names)                      # Add TaxonName objects
        session.commit()                            # Save changes

# Only run population if executed directly (not imported)
if __name__ == "__main__":
    populate_database()
