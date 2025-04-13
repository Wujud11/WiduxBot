from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from settings_manager import SettingsManager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
settings = SettingsManager()

@router.get("/responses")
async def response_settings(request: Request):
    responses = settings.get_setting("custom_responses") or {}
    return templates.TemplateResponse("responses.html", {"request": request, "responses": responses})

@router.post("/save_responses")
async def save_responses(
    request: Request,
    mention_responses: str = Form(...),
    timeout_warning: str = Form(...),
    timeout_message: str = Form(...),
    taunts: str = Form(...),
    doom_fail: str = Form(...),
    doom_win: str = Form(...),
    team_win: str = Form(...),
    solo_win: str = Form(...),
    taunts_leader: str = Form(...),
    taunts_lose: str = Form(...),
    taunts_negative: str = Form(...),
    steal_victim: str = Form(...),
    sabotage_victim: str = Form(...),
):
    responses = {
        "mention_responses": [x.strip() for x in mention_responses.split(",") if x.strip()],
        "timeout_warning": timeout_warning.strip(),
        "timeout_message": timeout_message.strip(),
        "taunts": [x.strip() for x in taunts.split(",") if x.strip()],
        "doom_fail": [x.strip() for x in doom_fail.split(",") if x.strip()],
        "doom_win": [x.strip() for x in doom_win.split(",") if x.strip()],
        "team_win": [x.strip() for x in team_win.split(",") if x.strip()],
        "solo_win": [x.strip() for x in solo_win.split(",") if x.strip()],
        "taunts_leader": [x.strip() for x in taunts_leader.split(",") if x.strip()],
        "taunts_lose": [x.strip() for x in taunts_lose.split(",") if x.strip()],
        "taunts_negative": [x.strip() for x in taunts_negative.split(",") if x.strip()],
        "steal_victim": [x.strip() for x in steal_victim.split(",") if x.strip()],
        "sabotage_victim": [x.strip() for x in sabotage_victim.split(",") if x.strip()],
    }

    settings.update_setting("custom_responses", responses)
    return RedirectResponse(url="/responses", status_code=303)
