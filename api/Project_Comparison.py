import json


def compute_project_metrics(project_data):
    ground_floor_area = project_data['landArea'] * project_data['ground_percentage']
    repeated_floor_area = project_data['landArea'] * project_data['technical_percentage']
    roof_floor_area = repeated_floor_area * project_data['roof_floor_percentage']

    total_built_area = (
        ground_floor_area
        + repeated_floor_area * project_data['firstTypeFloors']
        + roof_floor_area
    )

    total_built_area *= project_data.get('totalBuildings', 1)

    shared_area = 0.10 * total_built_area
    effective_area = total_built_area - shared_area

    land_cost = project_data['landArea'] * project_data['landPrice']

    construction_cost = effective_area * project_data['constructionCostPerSqm']

    parking_cost_total = (
        project_data.get('parkingCost', 0)
        * project_data['landArea']
        * project_data.get('basementFloors', 1)
        * project_data.get('totalBuildings', 1)
    )

    shared_areas_cost_total = shared_area * project_data.get('sharedAreasCost', 0)

    direct_build_cost = construction_cost + parking_cost_total + shared_areas_cost_total

    total_project_cost = land_cost + direct_build_cost

    potential_sale_revenue = effective_area * project_data['sellingPrice1']

    sales_commission = (project_data['salesCommissionPct'] / 100.0) * potential_sale_revenue

    total_project_cost_with_commission = total_project_cost + sales_commission

    sale_gross_profit = potential_sale_revenue - total_project_cost_with_commission
    sale_gross_margin = 0.0
    if total_project_cost_with_commission > 0:
        sale_gross_margin = (sale_gross_profit / total_project_cost_with_commission) * 100.0

    annual_rental_revenue = effective_area * project_data['rentalPrice1']
    operating_expenses = 0.05 * annual_rental_revenue  # افتراض مصاريف تشغيلية 5%
    net_annual_rent = annual_rental_revenue - operating_expenses

    rental_roi_percent = 0.0
    if total_project_cost_with_commission > 0:
        rental_roi_percent = (net_annual_rent / total_project_cost_with_commission) * 100.0

    return {
        "المساحات": {
            "مساحة_الدور_الأرضي": ground_floor_area,
            "مساحة_الدور_المتكرر": repeated_floor_area,
            "مساحة_الملحق_العلوي": roof_floor_area,
            "إجمالي_المساحة_المبنية": total_built_area,
            "المساحة_المشتركة": shared_area,
            "المساحة_الفعالة": effective_area
        },
        "التكاليف": {
            "تكلفة_الأرض": land_cost,
            "تكلفة_البناء_المباشرة": direct_build_cost,
            "التكلفة_الإجمالية_بدون_عمولة": total_project_cost,
            "عمولة_البيع": sales_commission,
            "التكلفة_الإجمالية_مع_العمولة": total_project_cost_with_commission
        },
        "مؤشرات_البيع": {
            "عوائد_البيع_المحتملة": potential_sale_revenue,
            "إجمالي_الربح_من_البيع": sale_gross_profit,
            "هامش_الربح_من_البيع_٪": sale_gross_margin
        },
        "مؤشرات_الإيجار": {
            "الإيجار_السنوي": annual_rental_revenue,
            "صافي_الإيجار_السنوي": net_annual_rent,
            "عائد_الإيجار_٪": rental_roi_percent
        }
    }


def compare_two_projects_as_json(project1, project2):
    result1 = compute_project_metrics(project1)
    result2 = compute_project_metrics(project2)

    sale_margin_winner = 1 if result1["مؤشرات_البيع"]['هامش_الربح_من_البيع_٪'] > result2["مؤشرات_البيع"]['هامش_الربح_من_البيع_٪'] else 2

    rental_roi_winner = 1 if result1["مؤشرات_الإيجار"]['عائد_الإيجار_٪'] > result2["مؤشرات_الإيجار"]['عائد_الإيجار_٪'] else 2

    comparison_data = {
        "المشروع_الأول": result1,
        "المشروع_الثاني": result2,
        "تحليل_المقارنة": {
            "الأعلى_في_هامش_ربح_البيع": f"المشروع رقم {sale_margin_winner}",
            "الأعلى_في_عائد_الإيجار": f"المشروع رقم {rental_roi_winner}"
        }
    }

    return json.dumps(comparison_data, ensure_ascii=False, indent=2)

def start_comparison(project_1_data, project_2_data):
    # Compare the two
    comparison_result = compare_two_projects_as_json(project_1_data, project_2_data)

    return comparison_result
