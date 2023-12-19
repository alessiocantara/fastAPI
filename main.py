import io
import requests
from fastapi import APIRouter, FastAPI, HTTPException, Request  # Add the Request import
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from Bio import PDB
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.resources import CDN
from bokeh.embed import file_html
import numpy as np

router = APIRouter()

app = FastAPI(
    title="...",
)
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your React app's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PDBRequest(BaseModel):
    pdb_id: str

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

@app.post("/calculate_ramachandran", response_class=HTMLResponse)
async def calculate_ramachandran(request: PDBRequest):
    pdb_id = request.pdb_id

    # Fetch PDB file
    pdb_file = fetch_pdb_file(pdb_id)

    if pdb_file:
        # Parse PDB file
        parser = PDB.PDBParser(QUIET=True)
        structure = parser.get_structure("protein", io.StringIO(pdb_file))

        # Calculate phi-psi angles
        phi_angles, psi_angles = calculate_phi_psi_angles(structure)

        # Plot Ramachandran plot and return HTML
        html_content = plot_ramachandran(phi_angles, psi_angles, pdb_id)
        return HTMLResponse(content=html_content)
    else:
        raise HTTPException(status_code=404, detail="Failed to fetch PDB file")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "data": data})

# Your existing routes and app setup go here

app.include_router(router)
