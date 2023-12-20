from fastapi import FastAPI
from fastapi import APIRouter, FastAPI
from fastapi.responses import HTMLResponse
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.embed import file_html
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from bokeh.resources import CDN
import numpy as np
from Bio import PDB
import requests
from fastapi.staticfiles import StaticFiles

#culo

router = APIRouter()

app = FastAPI(
    title="...",
)
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_pdb_file(pdb_id):
    pdb_url = f'https://files.rcsb.org/download/{pdb_id}.pdb'
    try:
        response = requests.get(pdb_url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except:
        return None
    

def calculate_phi_psi_angles(structure):
    phi_angles = []
    psi_angles = []

    for model in structure:
        for chain in model:
            polypeptides = PDB.PPBuilder().build_peptides(chain)
            for poly_amino in polypeptides:
                phi_psi_angles = poly_amino.get_phi_psi_list()

                for phi_psi in phi_psi_angles:
                    phi, psi = phi_psi
                    if phi is not None and psi is not None:
                        phi_angles.append(np.degrees(phi))
                        psi_angles.append(np.degrees(psi))

    return phi_angles, psi_angles

def plot_ramachandran(phi_angles, psi_angles, pdb_file_path):
    source = ColumnDataSource(data=dict(phi=phi_angles, psi=psi_angles))

    plot = figure(title=f'Ramachandran Plot of {pdb_file_path}', width=800, height=600)

    # Draw dividing lines
    plot.line([0, 0], [-180, 180], line_color='black', line_dash='dashed', line_width=1)
    plot.line([-180, 180], [0, 0], line_color='black', line_dash='dashed', line_width=1)

    # Scatter plot
    plot.circle('phi', 'psi', source=source, size=5, alpha=0.5)

    # Set plot limits
    plot.xaxis.axis_label = 'Phi (ϕ) Angle'
    plot.yaxis.axis_label = 'Psi (ψ) Angle'
    plot.xaxis.bounds = (-180, 180)
    plot.yaxis.bounds = (-180, 180)

    # Add quadrant lines
    plot.line([-180, 180], [0, 0], line_color='black', line_width=1)
    plot.line([0, 0], [-180, 180], line_color='black', line_width=1)

    # Add quadrant labels at the intersection of lines
    plot.text(x=[-20, 20, -20], y=[10, 10, -180],
              text=['β sheet', 'L-α helix', 'R-α helix'],
              text_color='black', text_font_size='12pt', text_align='center', text_baseline='middle')

    return file_html(plot, CDN, f"Ramachandran Plot of {pdb_file_path}")


@app.get("/pdb/{pdb_id}", response_class=HTMLResponse)
def get_pdb_entry(pdb_id:str):
    pdb_content = fetch_pdb_file(pdb_id)
    if pdb_content is not None:
        # Perform analysis using the fetched PDB content
        parser = PDB.PDBParser(QUIET=True)
        structure = parser.get_structure('protein', pdb_content)

        phi_angles, psi_angles = calculate_phi_psi_angles(structure)
        return HTMLResponse(content=f"<html><head>{plot_ramachandran(phi_angles, psi_angles, pdb_id)}</head></html>")
    else:
        return HTMLResponse(content="<html><body>Error: Unable to fetch PDB file.</body></html>")

    
@app.get("/", response_class=HTMLResponse)
def read_root(pdb_id: str = input('PDB ID: ')):
    # Allow user to input PDB ID as a query parameter, default to '1ah9' if not provided
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure('protein', f'https://files.rcsb.org/download/{pdb_id}.pdb')

    phi_angles, psi_angles = calculate_phi_psi_angles(structure)
    return HTMLResponse(content=f"<html><head>{plot_ramachandran(phi_angles, psi_angles, pdb_id)}</head></html>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)