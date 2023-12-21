import json
import numpy as np

from bokeh.plotting import figure
from bokeh.embed import json_item
from bokeh.models import ColumnDataSource
from Bio import PDB


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


def plot_ramachandran(structure, pdb_file_path):
    phi_angles, psi_angles = calculate_phi_psi_angles(structure)

    source = ColumnDataSource(data=dict(phi=phi_angles, psi=psi_angles))

    plot = figure(
        title=f'Ramachandran Plot of {pdb_file_path}', width=800, height=600)
    plot.output_backend = "svg"

    # Draw dividing lines
    plot.line([0, 0], [-180, 180], line_color='black',
              line_dash='dashed', line_width=1)
    plot.line([-180, 180], [0, 0], line_color='black',
              line_dash='dashed', line_width=1)

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

    return json.dumps(json_item(plot))
