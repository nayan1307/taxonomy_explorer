# Taxonomy Explorer Web App

I am Nayan Chaudhari. This project was developed as part of my BINF6200 Bioinformatics Programming course at Northeastern University for my MS in Bioinformatics program.

---

## Overview

Taxonomy Explorer is a full-stack web application that enables users to explore taxonomy data (NCBI-style) using a searchable, navigable interface. It combines a FastAPI backend with a Dash frontend for interactive exploration of taxonomic hierarchies.

---

## Features

- Search taxa by keyword (contains, starts with, ends with)
- View taxon details: rank, parent, children, and names
- Navigate via clickable Taxon IDs
- Error handling and pagination
- Clean and responsive light-themed UI

---

## Project Structure

```
taxonomy_explorer/
├── README.md
├── requirements.txt
├── taxonomy.db
│
├── app/
│   ├── __init__.py
│   ├── api.py
│   ├── database.py
│   ├── models.py
│   ├── populate.py
│   └── __pycache__/
│
├── data/
│   ├── small_nodes.dmp
│   └── small_names.dmp
│
├── frontend/
│   ├── app.py
│   └── __pycache__/
```

---

## Required Input Data Format

The application expects two NCBI-style files located in the `data/` directory:

### small_nodes.dmp
Defines the taxonomic hierarchy.

**Expected format:**
```
tax_id	|	parent_tax_id	|	rank	|
```

**Example:**
```
9606	|	9605	|	species	|
```

### small_names.dmp
Contains all names and synonyms associated with each taxon.

**Expected format:**
```
tax_id	|	name_txt	|	unique_name	|	name_class	|
```

**Example:**
```
9606	|	Homo sapiens	|		|	scientific name	|
```

Important Note: Format must exactly match NCBI dumps.

---

## Setup Instructions

### 1. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Populate the database
```bash
python app/populate.py
```

This creates `taxonomy.db` using the `.dmp` files in `data/`.

---

## Running the App

### Start the FastAPI backend in one terminal
```bash
uvicorn app.api:app --reload
```

### Start the Dash frontend in another terminal
```bash
python frontend/app.py
```

Open your browser and go to:  
http://127.0.0.1:8050

Note: Virtual Environment needs to be enabled for the packages to work.
---

## Reproducibility Checklist

- [x] Python version ≥ 3.8
- [x] Virtual environment setup
- [x] Input files match NCBI format
- [x] `populate.py` populates a reproducible SQLite DB
- [x] README contains full setup and usage instructions
- [x] Requirements listed in `requirements.txt`

---

## Test Cases

- Search for "Homo" → Returns expected results
- Click taxon ID → Navigates to taxon detail
- Navigate to invalid ID → Graceful error
- Pagination works for more than 10 results
- Handles empty search input correctly

---

## NOTE:
For video help on how it function here is the YouTube link
https://www.youtube.com/watch?v=DR_su3BeG1w

---

## Course & Credits

**Course:** BINF6200 - Bioinformatics Programming  
**Institution:** Northeastern University  
**Program:** MS in Bioinformatics  
**Professor:** Dr. Wan Quan