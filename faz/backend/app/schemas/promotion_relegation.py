# app/schemas/promotion_relegation.py
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class PromotionRelegationRuleBase(BaseModel):
    from_league_id: UUID
    to_league_id: UUID
    positions_promoted: int = 2
    positions_relegated: int = 2
    season: str

class PromotionRelegationRuleCreate(PromotionRelegationRuleBase):
    pass

class PromotionRelegationRuleOut(PromotionRelegationRuleBase):
    id: UUID

    class Config:
        from_attributes = True

class PromotionRelegationBase(BaseModel):
    team_id: UUID
    from_league_id: UUID
    to_league_id: UUID
    season: str
    action: str

class PromotionRelegationCreate(PromotionRelegationBase):
    pass

class PromotionRelegationOut(PromotionRelegationBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True