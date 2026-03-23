from datetime import date

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select, insert, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.services.analytics import AnalyticsService
from app.shemas import (
    ClosedCreditResponse,
    OpenCreditResponse,
    PlanPerformance,
    MonthlyAnalytics,
    YearlyAnalyticsResponse,
)
from app.models import Credit, Plan, Payment, User
from app.database import get_db

router = APIRouter()


@router.get("/user_credits/{user_id}")
async def get_user_credits(user_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(Credit)
        .where(Credit.user_id == user_id)
        .options(selectinload(Credit.payments))
    )

    user_query = select(User).where(User.id == user_id)
    user_res = await db.execute(user_query)
    user = user_res.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(query)
    credits_list = result.scalars().all()

    response = []
    today = date.today()

    for credit in credits_list:
        body_paid = sum(p.sum for p in credit.payments if p.type_id == 1)
        percent_paid = sum(p.sum for p in credit.payments if p.type_id == 2)

        if credit.actual_return_date:
            response.append(
                ClosedCreditResponse(
                    issuance_date=credit.issuance_date,
                    is_closed=True,
                    actual_return_date=credit.actual_return_date,
                    body=credit.body,
                    percent=credit.percent,
                    total_payments=body_paid + percent_paid,
                )
            )
        else:
            overdue = (
                (today - credit.return_date).days if today > credit.return_date else 0
            )

            response.append(
                OpenCreditResponse(
                    issuance_date=credit.issuance_date,
                    is_closed=False,
                    return_date=credit.return_date,
                    overdue_days=overdue,
                    body=credit.body,
                    percent=credit.percent,
                    body_payments=body_paid,
                    percent_payments=percent_paid,
                )
            )

    return response


@router.post("/plans_insert")
async def create_plans_insert(
    plans_insert: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    try:
        df = pd.read_excel(plans_insert.file)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Excel file format")

    headers = ["sum", "period", "category"]
    category_map = {"видача": 3, "збір": 4}
    query = select(Plan)
    result = await db.execute(query)
    plans = result.scalars().all()

    df["category"] = df["category"].str.lower().str.strip()

    if not df["category"].isin(category_map.keys()).all():
        unknown = df[~df["category"].isin(category_map.keys())]["category"].unique()
        raise HTTPException(
            status_code=400, detail=f"Unknown categories: {list(unknown)}"
        )

    if df.empty:
        raise HTTPException(status_code=400, detail="The file is empty")

    if not set(headers).issubset(df.columns):
        raise HTTPException(
            status_code=400, detail=f"Missing columns. Required: {headers}"
        )

    df["period"] = pd.to_datetime(df["period"])
    if (df["period"].dt.day != 1).any():
        raise HTTPException(
            status_code=400,
            detail="All plan periods must start on the 1st day",
        )

    df["period"] = df["period"].dt.date

    if (df["sum"] < 0).any() or df["sum"].isna().any():
        raise HTTPException(
            status_code=400, detail="Sum must be a positive number and cannot be empty"
        )

    if df.duplicated(subset=["period", "category"]).any():
        raise HTTPException(status_code=400, detail="Duplicate dates are not allowed")

    existing_set = {(p.period, p.category_id) for p in plans}

    df["category_id"] = df["category"].map(category_map)
    for index, row in df.iterrows():
        if (row["period"], row["category_id"]) in existing_set:
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate found: Period {row['period']} and Category {row['category_id']} already in DB",
            )

    final_columns = ["sum", "period", "category_id"]
    data_to_insert = df[final_columns].to_dict(orient="records")
    await db.execute(insert(Plan), data_to_insert)
    await db.commit()

    return {"message": f"Successfully uploaded {len(data_to_insert)} plans"}


@router.get("/plans_performance")
async def get_plans_performance(
    plan_date: date = None, db: AsyncSession = Depends(get_db)
):

    month_start = plan_date.replace(day=1)
    category_names = {3: "видача", 4: "збір"}

    query = select(Plan).where(Plan.period == month_start)
    result = await db.execute(query)
    plans = result.scalars().all()

    performance_report = []

    for plan in plans:
        fact_sum = 0.0

        if plan.category_id == 3:
            query_fact = select(func.sum(Credit.body)).where(
                Credit.issuance_date >= month_start, Credit.issuance_date <= plan_date
            )
            res_fact = await db.execute(query_fact)
            fact_sum = res_fact.scalar() or 0.0
        elif plan.category_id == 4:
            query_fact = select(func.sum(Payment.sum)).where(
                Payment.payment_date >= month_start, Payment.payment_date <= plan_date
            )

            res_fact = await db.execute(query_fact)
            fact_sum = res_fact.scalar() or 0.0

        precent = (fact_sum / plan.sum * 100) if plan.sum > 0 else 0.0

        performance_report.append(
            PlanPerformance(
                period=plan.period,
                category_id=plan.category_id,
                category_name=category_names.get(plan.category_id),
                fact_sum=fact_sum,
                plan_sum=plan.sum,
                performance_percent=round(precent, 2),
            )
        )
    return performance_report


@router.get("/year_performance", response_model=YearlyAnalyticsResponse)
async def get_yearly_analytics(year: int, db: AsyncSession = Depends(get_db)):
    plans_res = await db.execute(select(Plan).where(extract("year", Plan.period) == year))
    plans = plans_res.scalars().all()

    credits_res = await db.execute(
        select(
            extract("month", Credit.issuance_date).label("month"),
            func.count(Credit.id).label("count"),
            func.sum(Credit.body).label("sum"),
        ).where(extract("year", Credit.issuance_date) == year).group_by("month")
    )
    credits_data = {int(r.month): r for r in credits_res.all()}

    payments_res = await db.execute(
        select(
            extract("month", Payment.payment_date).label("month"),
            func.count(Payment.id).label("count"),
            func.sum(Payment.sum).label("sum"),
        ).where(extract("year", Payment.payment_date) == year).group_by("month")
    )
    payments_data = {int(r.month): r for r in payments_res.all()}

    # 2. Отримуємо список словників від сервісу (чиста математика)
    raw_results = AnalyticsService.calculate_yearly_data(
        year, plans, credits_data, payments_data
    )

    # 3. ФІКСАЦІЯ: Перетворюємо словники в об'єкти MonthlyAnalytics
    # Це гарантує, що якщо сервіс щось порахував не так, Pydantic видасть помилку тут
    validated_data = [MonthlyAnalytics(**item) for item in raw_results]

    # 4. Повертаємо фінальну відповідь
    return YearlyAnalyticsResponse(year=year, data=validated_data)