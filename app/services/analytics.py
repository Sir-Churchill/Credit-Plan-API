from typing import List, Dict, Any


class AnalyticsService:
    @staticmethod
    def calculate_yearly_data(
            year: int,
            plans: List[Any],
            credits_data: Dict[int, Any],
            payments_data: Dict[int, Any]
    ) -> List[Dict[str, Any]]:
        total_issuance_year = sum(float(r.sum or 0) for r in credits_data.values())
        total_payments_year = sum(float(r.sum or 0) for r in payments_data.values())

        results = []
        for m in range(1, 13):
            plan_iss = next((p.sum for p in plans if p.period.month == m and p.category_id == 3), 0.0)
            plan_pay = next((p.sum for p in plans if p.period.month == m and p.category_id == 4), 0.0)

            f_iss = credits_data.get(m)
            f_pay = payments_data.get(m)

            iss_sum = float(f_iss.sum) if f_iss else 0.0
            pay_sum = float(f_pay.sum) if f_pay else 0.0

            results.append({
                "month_year": f"{m:02d}.{year}",
                "issuance_count": f_iss.count if f_iss else 0,
                "issuance_plan_sum": plan_iss,
                "issuance_fact_sum": iss_sum,
                "issuance_performance": round((iss_sum / plan_iss * 100), 2) if plan_iss > 0 else 0.0,
                "issuance_share_of_year": round((iss_sum / total_issuance_year * 100),
                                                2) if total_issuance_year > 0 else 0.0,

                "payments_count": f_pay.count if f_pay else 0,
                "payments_plan_sum": plan_pay,
                "payments_fact_sum": pay_sum,
                "payments_performance": round((pay_sum / plan_pay * 100), 2) if plan_pay > 0 else 0.0,
                "payments_share_of_year": round((pay_sum / total_payments_year * 100),
                                                2) if total_payments_year > 0 else 0.0,
            })
        return results