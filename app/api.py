# Import necessary modules from FastAPI, SQLModel, and SQLAlchemy
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from sqlalchemy import func
from typing import Optional

# Import local modules
from app.database import create_db_and_tables, engine
from app.models import Taxon, TaxonName

# Initialize FastAPI application
app = FastAPI(title="Taxonomy Explorer API")

# Create tables on application startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Taxonomy API is up and running!"}

# Endpoint to retrieve detailed information for a specific taxon
@app.get("/taxa")
def get_taxon(tax_id: int = Query(..., description="NCBI Taxonomy ID")):
    with Session(engine) as session:
        # Look up the taxon
        taxon = session.get(Taxon, tax_id)
        if not taxon:
            raise HTTPException(status_code=404, detail="Taxon not found")

        # Get parent taxon info (if it exists)
        parent_name = None
        if taxon.parent_tax_id:
            parent = session.get(Taxon, taxon.parent_tax_id)
            if parent:
                sci_name = session.exec(
                    select(TaxonName)
                    .where(TaxonName.tax_id == parent.tax_id)
                    .where(TaxonName.name_class == "scientific name")
                ).first()
                parent_name = {
                    "tax_id": parent.tax_id,
                    "scientific_name": sci_name.name_txt if sci_name else None
                }

        # Get all associated names
        names = session.exec(
            select(TaxonName).where(TaxonName.tax_id == tax_id)
        ).all()
        names_list = [
            {
                "name": n.name_txt,
                "class": n.name_class,
                "is_scientific": n.name_class == "scientific name"
            } for n in names
        ]

        # Get all children of the taxon
        children = session.exec(
            select(Taxon).where(Taxon.parent_tax_id == tax_id)
        ).all()
        children_list = []
        for child in children:
            child_name = session.exec(
                select(TaxonName)
                .where(TaxonName.tax_id == child.tax_id)
                .where(TaxonName.name_class == "scientific name")
            ).first()
            children_list.append({
                "tax_id": child.tax_id,
                "rank": child.rank,
                "scientific_name": child_name.name_txt if child_name else None
            })

        # Construct and return taxon info
        return {
            "tax_id": taxon.tax_id,
            "rank": taxon.rank,
            "parent": parent_name,
            "names": names_list,
            "children": children_list
        }

# Endpoint to search for taxon names based on a keyword
@app.get("/search")
def search_taxa(
    keyword: str = Query(..., description="Search keyword"),
    search_mode: str = Query("contains", enum=["contains", "starts with", "ends with"]),
    page: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=100)
):
    with Session(engine) as session:
        # Build filter expression based on search mode
        if search_mode == "contains":
            filter_expr = TaxonName.name_txt.contains(keyword)
        elif search_mode == "starts with":
            filter_expr = TaxonName.name_txt.startswith(keyword)
        elif search_mode == "ends with":
            filter_expr = TaxonName.name_txt.endswith(keyword)

        # Get total count for pagination
        count_stmt = select(func.count()).select_from(TaxonName).where(filter_expr)
        total = session.exec(count_stmt).one()

        # Fetch the current page of results
        stmt = (
            select(TaxonName)
            .where(filter_expr)
            .offset((page - 1) * items_per_page)
            .limit(items_per_page)
        )
        results = session.exec(stmt).all()

        # Format results
        data = [
            {
                "tax_id": r.tax_id,
                "name": r.name_txt,
                "class": r.name_class
            } for r in results
        ]

        return {
            "results": data,
            "total": total,
            "page": page,
            "items_per_page": items_per_page
        }
