from datetime import date
from typing import List

from pydantic import BaseModel


class CreditBase(BaseModel):
    issuance_date: date
    is_closed: bool
    body: float
    percent: float

    class Config:
        from_attributes = True


class ClosedCreditResponse(CreditBase):
    actual_return_date: date
    total_payments: float


class OpenCreditResponse(CreditBase):
    return_date: date
    overdue_days: int
    body_payments: float
    percent_payments: float


class PlanPerformance(BaseModel):
    period: date
    category_id: int
    category_name: str
    plan_sum: float
    fact_sum: float
    performance_percent: float


class MonthlyAnalytics(BaseModel):
    month_year: str
    issuance_count: int
    issuance_plan_sum: float
    issuance_fact_sum: float
    issuance_performance: float
    issuance_share_of_year: float
    payments_count: int
    payments_plan_sum: float
    payments_fact_sum: float
    payments_performance: float
    payments_share_of_year: float


class YearlyAnalyticsResponse(BaseModel):
    year: int
    data: List[MonthlyAnalytics]
