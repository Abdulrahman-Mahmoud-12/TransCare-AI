from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Initialize the router without a prefix since it handles the root URL "/"
router = APIRouter(tags=["Home"])

# Point to your templates directory
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    """
    Renders and serves the RetailIQ Landing Homepage.
    """
    return templates.TemplateResponse(
        request=request,
        name="home.html", 
        context={"request": request}
    )