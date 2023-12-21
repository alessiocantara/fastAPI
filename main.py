import io
import requests

from fastapi import APIRouter, FastAPI, HTTPException  # Add the Request import
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from Bio import PDB

from plots import plot_ramachandran

app = FastAPI(
    title="Ramachandran Plot API",
)
router = APIRouter()
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")


def fetch_pdb_file(pdb_id):
    pdb_url = f'https://files.rcsb.org/download/{pdb_id}.pdb'
    try:
        response = requests.get(pdb_url)
        if response.status_code == 200:
            return response.text
    except:
        return None


@app.get("/calculate_ramachandran/{pdb_id}", response_class=HTMLResponse)
async def calculate_ramachandran(pdb_id: str):
    pdb_file = fetch_pdb_file(pdb_id)

    if pdb_file is None:
        raise HTTPException(status_code=404, detail="Failed to fetch PDB file")

    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("protein", io.StringIO(pdb_file))

    return plot_ramachandran(structure, pdb_id)
