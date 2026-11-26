from fastapi import APIRouter, Depends
from app.core.security import Principal, current_principal
from .data import ORGANIZATION

router = APIRouter(prefix="/organization", tags=["organization"])

@router.get("")
def organization(q: str = "", _: Principal = Depends(current_principal)):
    data = {**ORGANIZATION, "areas": list(ORGANIZATION["areas"])}
    if q.strip():
        term = q.casefold().strip()
        data["areas"] = [area for area in data["areas"] if term in " ".join([area["name"], area["manager"]["title"], area["manager"]["name"], *[team["title"] for team in area["teams"]], *[name for team in area["teams"] for name in team["members"]]]).casefold()]
    people = set(item["name"] for item in ORGANIZATION["leadership"])
    for area in ORGANIZATION["areas"]:
        people.add(area["manager"]["name"])
        for team in area["teams"]: people.update(team["members"])
    return {**data, "total_people": len(people)}
