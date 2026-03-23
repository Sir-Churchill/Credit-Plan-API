import logging
import os
import numpy as np
import pandas as pd
from sqlalchemy import insert, delete, select, func

from app.database import AsyncSessionLocal
from app.models import Dictionary, User, Plan, Credit, Payment

IMPORT_CHART = [
    ("dictionary.csv", Dictionary),
    ("users.csv", User),
    ("plans.csv", Plan),
    ("credits.csv", Credit),
    ("payments.csv", Payment),
]


async def upload():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    async with AsyncSessionLocal() as session:
        for file_name, model_class in IMPORT_CHART:
            csv_path = os.path.join(current_dir, "..", "data_csv", file_name)

            if not os.path.exists(csv_path):
                logging.info(f"Пропущено: {file_name} не знайдено")
                continue

            try:

                result = await session.execute(
                    select(func.count()).select_from(model_class)
                )
                count = result.scalar()

                if count > 0:
                    logging.info(
                        f"Пропущено: {model_class.__tablename__} вже має дані ({count} записів)."
                    )
                    continue

                df = pd.read_csv(csv_path, sep="\t")
                if file_name == "credits.csv":
                    df = df.fillna(np.nan).replace([np.nan], [None])
                data = df.to_dict(orient="records")

                if data:
                    async with session.begin_nested():
                        await session.execute(delete(model_class))
                        await session.execute(insert(model_class), data)

                    await session.commit()
                    logging.info(f"{file_name} -> {model_class.__tablename__}")

            except Exception as e:
                logging.warn(f"Помилка у {file_name}: {e}")
                await session.rollback()
