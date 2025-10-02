from __future__ import annotations

from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from generations import generate_wizard_stats as generate_wizard_stats_from_description
from generations import generate_spells as generate_spells_for_wizard

app = FastAPI(title="Wizard Prompt Battle API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SpellModel(BaseModel):
    name: str
    description: str
    spell_type: str
    element: str
    strength: float


class WizardStatsModel(BaseModel):
    name: str
    primary_element: str
    secondary_element: str
    attack: float
    defense: float
    health: float
    healing: float
    arcane: float
    combat_style: str


class WizardDescriptionPayload(BaseModel):
    description: str = Field(..., min_length=1, description="Brief description of the wizard to generate")


class SpellGenerationPayload(BaseModel):
    description: str = Field(..., min_length=1)
    stats: WizardStatsModel


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate_wizard_stats", response_model=WizardStatsModel)
async def generate_wizard_stats(payload: WizardDescriptionPayload) -> WizardStatsModel:
    try:
        result = generate_wizard_stats_from_description(payload.description)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Model generation failed: {exc}") from exc

    return WizardStatsModel(**result)


@app.post("/generate_spells", response_model=List[SpellModel])
async def generate_spells(payload: SpellGenerationPayload) -> List[SpellModel]:
    try:
        result = generate_spells_for_wizard(payload.description, payload.stats.model_dump())
    except Exception as exc:  # noqa: BLE001
        print(exc)
        raise HTTPException(status_code=511, detail=f"Model generation failed: {exc}") from exc

    return [SpellModel(**spell) for spell in result]


def run() -> None:
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=3167, reload=True)


if __name__ == "__main__":
    run()
