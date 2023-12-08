import requests
from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request

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

@router.get("/go-terms/{id}")
def get_test(id: str):
    request_url = f"https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A{id}"
    r = requests.get(request_url, headers={"Accept": "application/json"})       
    data = r.json()
    return JSONResponse(data)

@router.get("/eco-terms/{id}")
def get_eco(id: str):
    request_url = f"https://www.ebi.ac.uk/QuickGO/services/ontology/eco/terms/ECO%3A{id}"
    r = requests.get(request_url, headers={"Accept": "application/json"})        
    data = r.json()
    return JSONResponse(data)

@router.get("/uniprot/{organism_id}")
def get_uni(organism_id: str):
    url = f"https://rest.uniprot.org/uniprotkb/search?query=organism_id:{organism_id}&format=json"
    response = requests.get(url).text    
    return response

@router.get("/pubmed/{id}")
def get_article_info(id):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": id,
        "retmode": "json"
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if id in data["result"]:
        article_info = data["result"][id]
        title = article_info["title"]
        article_url = f"https://pubmed.ncbi.nlm.nih.gov/{id}"
        return title, article_url
    return None, None


@router.get("/articles/{id}")
def get_article(id: str):
    title, article_url = get_article_info(id)
    if title and article_url:
        return {"Title": title, "URL": article_url}
    else:
        return {"error": f"No information found for PubMed ID: {id}"}

@app.get("/pdb/{id}")
def get_pdb_entry(id: str):
    base_url = "https://data.rcsb.org/rest/v1/core/entry"

    # Make a request to the PDB API
    url = f"{base_url}/{id}"
    response = requests.get(url)

    if response.status_code == 200:
        # Process the JSON response here
        entry_info = response.json()
        return {"id": id, "entry_info": entry_info}
    else:
        return {"error": "Failed to retrieve PDB entry"}

@router.get("/uniprot_single_entry/{id}")
def get_uniprot_info(id: str):
    url = f"https://rest.uniprot.org/uniprotkb/{id}.json"
    #url2 = f"https://www.uniprot.org/uniprotkb/{id}"
    response = requests.get(url, headers={"Accept": "application/json"})
    data = response.json()
    return JSONResponse(data)

@router.get("/emdb_annotation/{id}")
def get_emdb_annotation(id: str):
    url = f"https://www.ebi.ac.uk/emdb/api/annotations/{id}"
    response = requests.get(url, headers={"Accept": "application/json"})
    data = response.json()
    return JSONResponse(data)
    
    
    
data = { "root": [ {"kind": "emdb_annotation", "id": ""}, {"kind": "uniprot_single", "id": ""}, { "kind": "uniprot", "id": "", "organism_id": "" }, { "kind": "pdb", "id": "" }, { "kind": "go", "id":""}, { "kind": "pubmed", "id": ""}, { "kind": "eco", "id": ""} ] }

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "data": data})
@router.post("/update")
async def update_data(kind: str, id: str):
    for item in data["root"]:
        if item["kind"] == kind:
            item["id"] = id
            break
    return JSONResponse({"message": "Data updated successfully"})

@router.get("/data")
def get_data():
    return JSONResponse(data)

app.include_router(router)

