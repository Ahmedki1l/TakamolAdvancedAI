# def compute_project_metrics(project_data):
#     """
#     Computes key metrics (effective area, sale revenues, rental revenues, ROI, etc.)
#     for a given real-estate project.
#
#     Expected keys in 'project_data':
#       - 'landArea' (float): total land area
#       - 'ground_percentage' (float): e.g. 0.6
#       - 'technical_percentage' (float): e.g. 0.75
#       - 'roof_floor_percentage' (float): e.g. 0.5
#       - 'no_of_floors' (int)
#       - 'firstTypeFloors' (int)
#       - 'secondFloors' (int)        # if used
#       - 'constructionCostPerSqm' (float)
#       - 'parkingCost' (float)
#       - 'sharedAreasCost' (float)
#       - 'salesCommissionPct' (float)  # e.g. 5
#       - 'sellingPrice1' (float)       # e.g. 27000
#       - 'rentalPrice1' (float)        # e.g. 900
#       - 'landPrice' (float)           # e.g. 10000 for the land cost per sqm
#       - 'totalBuildings' (float)      # if a multi-building project (else just 1)
#       ... and so on, depending on your formula
#
#     Returns a dictionary with:
#       - 'effective_area'
#       - 'total_project_cost'
#       - 'potential_sale_revenue'
#       - 'sale_gross_profit'
#       - 'sale_gross_margin'
#       - 'annual_rental_revenue'
#       - 'net_annual_rent'
#       - 'rental_roi_percent'
#     """
#
#     # 1) Derive net floor areas
#     ground_floor_area = project_data['landArea'] * project_data['ground_percentage']
#     repeated_floor_area = project_data['landArea'] * project_data['technical_percentage']
#     roof_floor_area = repeated_floor_area * project_data['roof_floor_percentage']
#
#     # For simplicity, assume firstTypeFloors is the number of repeated floors using repeated_floor_area
#     # secondFloors if needed – depends on your project logic
#     # Or, if you do 3 floors total => ground + 2 repeated, etc.
#     total_built_area = (
#         ground_floor_area
#         + repeated_floor_area * project_data['firstTypeFloors']
#         + roof_floor_area
#     )
#
#     # If project includes multiple buildings, multiply
#     # (If your data says totalBuildings = 1 for single buildings, no change)
#     total_built_area *= project_data.get('totalBuildings', 1)
#
#     # Example: 10% shared, or your data might define it differently
#     shared_area = 0.10 * total_built_area
#     effective_area = total_built_area - shared_area
#
#     # 2) Land costs
#     land_cost = project_data['landArea'] * project_data['landPrice']
#
#     # 3) Construction costs (a rough approach; adapt to your actual formula)
#     #    For example, we might say cost = effective_area * constructionCostPerSqm
#     #    plus some parking cost, plus sharedAreasCost * shared_area, etc.
#     construction_cost = effective_area * project_data['constructionCostPerSqm']
#     parking_cost_total = (project_data.get('parkingCost', 0) *
#                           project_data['landArea'] *
#                           project_data.get('basementFloors', 1) *
#                           project_data.get('totalBuildings', 1))
#     shared_areas_cost_total = shared_area * project_data.get('sharedAreasCost', 0)
#
#     # Summing up direct building costs (this is a simplified approach)
#     direct_build_cost = construction_cost + parking_cost_total + shared_areas_cost_total
#
#     # 4) Total project cost = land cost + direct building cost
#     total_project_cost = land_cost + direct_build_cost
#
#     # 5) Potential sale revenue
#     potential_sale_revenue = effective_area * project_data['sellingPrice1']
#     sales_commission = (project_data['salesCommissionPct'] / 100.0) * potential_sale_revenue
#     # If your dataset includes commission as part of the cost, add it:
#     total_project_cost_with_commission = total_project_cost + sales_commission
#
#     # 6) Sale profit and margin
#     sale_gross_profit = potential_sale_revenue - total_project_cost_with_commission
#     sale_gross_margin = 0.0
#     if total_project_cost_with_commission > 0:
#         sale_gross_margin = (sale_gross_profit / total_project_cost_with_commission) * 100.0
#
#     # 7) Rental revenues
#     annual_rental_revenue = effective_area * project_data['rentalPrice1']
#     # Operating expenses example (5% of annual revenue) – adapt to your real logic
#     operating_expenses = 0.05 * annual_rental_revenue
#     net_annual_rent = annual_rental_revenue - operating_expenses
#
#     # 8) Simple rental ROI
#     rental_roi_percent = 0.0
#     if total_project_cost_with_commission > 0:
#         rental_roi_percent = (net_annual_rent / total_project_cost_with_commission) * 100.0
#
#     return {
#         'effective_area': effective_area,
#         'total_project_cost': total_project_cost_with_commission,
#         'potential_sale_revenue': potential_sale_revenue,
#         'sale_gross_profit': sale_gross_profit,
#         'sale_gross_margin': sale_gross_margin,
#         'annual_rental_revenue': annual_rental_revenue,
#         'net_annual_rent': net_annual_rent,
#         'rental_roi_percent': rental_roi_percent
#     }
#
#
# def compare_two_projects(project1, project2):
#     """
#     Computes metrics for project1 and project2, then prints out a
#     summarized comparison.
#     """
#     result1 = compute_project_metrics(project1)
#     result2 = compute_project_metrics(project2)
#
#     # Let’s build a textual comparison
#     comparison_lines = []
#     comparison_lines.append("====== مقارنة بين المشروعين ======\n")
#
#     comparison_lines.append("نتائج المشروع الأول:")
#     comparison_lines.append(f"  - المساحة الفعالة (م²): {result1['effective_area']:.1f}")
#     comparison_lines.append(f"  - التكلفة الإجمالية للمشروع (ريال): {result1['total_project_cost']:,.0f}")
#     comparison_lines.append(f"  - عوائد البيع المحتملة (ريال): {result1['potential_sale_revenue']:,.0f}")
#     comparison_lines.append(f"  - إجمالي الربح من البيع (ريال): {result1['sale_gross_profit']:,.0f}")
#     comparison_lines.append(f"  - هامش الربح من البيع (%): {result1['sale_gross_margin']:.1f}%")
#     comparison_lines.append(f"  - الإيجار السنوي (ريال): {result1['annual_rental_revenue']:,.0f}")
#     comparison_lines.append(f"  - صافي الإيجار السنوي (ريال): {result1['net_annual_rent']:,.0f}")
#     comparison_lines.append(f"  - نسبة العائد من الإيجار (%): {result1['rental_roi_percent']:.2f}%\n")
#
#     comparison_lines.append("نتائج المشروع الثاني:")
#     comparison_lines.append(f"  - المساحة الفعالة (م²): {result2['effective_area']:.1f}")
#     comparison_lines.append(f"  - التكلفة الإجمالية للمشروع (ريال): {result2['total_project_cost']:,.0f}")
#     comparison_lines.append(f"  - عوائد البيع المحتملة (ريال): {result2['potential_sale_revenue']:,.0f}")
#     comparison_lines.append(f"  - إجمالي الربح من البيع (ريال): {result2['sale_gross_profit']:,.0f}")
#     comparison_lines.append(f"  - هامش الربح من البيع (%): {result2['sale_gross_margin']:.1f}%")
#     comparison_lines.append(f"  - الإيجار السنوي (ريال): {result2['annual_rental_revenue']:,.0f}")
#     comparison_lines.append(f"  - صافي الإيجار السنوي (ريال): {result2['net_annual_rent']:,.0f}")
#     comparison_lines.append(f"  - نسبة العائد من الإيجار (%): {result2['rental_roi_percent']:.2f}%\n")
#
#     # You can add whichever logic you want here:
#     # e.g. which project yields higher sale margin, or higher rental ROI, etc.
#     sale_margin_winner = 1 if result1['sale_gross_margin'] > result2['sale_gross_margin'] else 2
#     rental_roi_winner = 1 if result1['rental_roi_percent'] > result2['rental_roi_percent'] else 2
#
#     comparison_lines.append("أي مشروع يحقق هامش ربح أعلى من البيع؟")
#     comparison_lines.append(f"  المشروع رقم {sale_margin_winner} لديه هامش ربح أعلى.\n")
#     comparison_lines.append("أي مشروع يحقق عائداً أعلى من الإيجار؟")
#     comparison_lines.append(f"  المشروع رقم {rental_roi_winner} لديه عائد إيجار أعلى.\n")
#
#     return "\n".join(comparison_lines)
import json


def compute_project_metrics(project_data):
    """
    تقوم هذه الدالة بحساب المؤشرات الأساسية (المساحات، التكاليف، مؤشرات البيع والإيجار)
    لمشروع عقاري اعتماداً على القيم المدخلة في قاموس (project_data).
    """

    # 1) حساب المساحات
    ground_floor_area = project_data['landArea'] * project_data['ground_percentage']
    repeated_floor_area = project_data['landArea'] * project_data['technical_percentage']
    roof_floor_area = repeated_floor_area * project_data['roof_floor_percentage']

    total_built_area = (
        ground_floor_area
        + repeated_floor_area * project_data['firstTypeFloors']
        + roof_floor_area
    )

    # إذا كان المشروع يحتوي على عدة مبانٍ، نضرب في عدد المباني
    total_built_area *= project_data.get('totalBuildings', 1)

    # نفترض أن المساحات المشتركة = 10% من إجمالي المساحة المبنية
    shared_area = 0.10 * total_built_area
    effective_area = total_built_area - shared_area

    # 2) التكاليف
    land_cost = project_data['landArea'] * project_data['landPrice']

    # تكلفة البناء الأساسية
    construction_cost = effective_area * project_data['constructionCostPerSqm']

    # تكلفة المواقف
    parking_cost_total = (
        project_data.get('parkingCost', 0)
        * project_data['landArea']
        * project_data.get('basementFloors', 1)
        * project_data.get('totalBuildings', 1)
    )

    # تكلفة المساحات المشتركة
    shared_areas_cost_total = shared_area * project_data.get('sharedAreasCost', 0)

    # مجموع تكاليف البناء المباشرة
    direct_build_cost = construction_cost + parking_cost_total + shared_areas_cost_total

    # التكلفة الإجمالية بدون عمولة
    total_project_cost = land_cost + direct_build_cost

    # 3) عوائد البيع
    potential_sale_revenue = effective_area * project_data['sellingPrice1']

    # عمولة البيع
    sales_commission = (project_data['salesCommissionPct'] / 100.0) * potential_sale_revenue

    # التكلفة الإجمالية مع العمولة
    total_project_cost_with_commission = total_project_cost + sales_commission

    # 4) مؤشرات البيع (الربح وهامش الربح)
    sale_gross_profit = potential_sale_revenue - total_project_cost_with_commission
    sale_gross_margin = 0.0
    if total_project_cost_with_commission > 0:
        sale_gross_margin = (sale_gross_profit / total_project_cost_with_commission) * 100.0

    # 5) مؤشرات الإيجار
    annual_rental_revenue = effective_area * project_data['rentalPrice1']
    operating_expenses = 0.05 * annual_rental_revenue  # افتراض مصاريف تشغيلية 5%
    net_annual_rent = annual_rental_revenue - operating_expenses

    rental_roi_percent = 0.0
    if total_project_cost_with_commission > 0:
        rental_roi_percent = (net_annual_rent / total_project_cost_with_commission) * 100.0

    # تنظيم النتائج في قاموس منسّق
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
    """
    تحسب المؤشرات لكل من المشروعين، وترجع النتيجة بصيغة JSON جاهزة للاستخدام في الواجهات الأمامية.
    """
    result1 = compute_project_metrics(project1)
    result2 = compute_project_metrics(project2)

    # حدد من يملك هامش ربح بيع أعلى
    sale_margin_winner = 1 if result1["مؤشرات_البيع"]['هامش_الربح_من_البيع_٪'] > result2["مؤشرات_البيع"]['هامش_الربح_من_البيع_٪'] else 2
    # حدد من يملك عائد إيجار أعلى
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


# if __name__ == "__main__":
#     # Example usage:
#     project_1_data = {
#         "landArea": 936.13435564,
#         "ground_percentage": 0.6,
#         "technical_percentage": 0.75,
#         "roof_floor_percentage": 0.5,
#         "no_of_floors": 3,
#         "firstTypeFloors": 2,
#         "secondFloors": 1,
#         "constructionCostPerSqm": 1800.0,
#         "parkingCost": 1000.0,
#         "sharedAreasCost": 300.0,
#         "salesCommissionPct": 5.0,
#         "sellingPrice1": 27000.0,
#         "rentalPrice1": 900.0,
#         "landPrice": 10000.0,
#         "totalBuildings": 1.0,
#         "basementFloors": 1
#     }
#
#     project_2_data = {
#         "landArea": 1200.0,
#         "ground_percentage": 0.65,
#         "technical_percentage": 0.70,
#         "roof_floor_percentage": 0.4,
#         "no_of_floors": 4,
#         "firstTypeFloors": 3,
#         "secondFloors": 0,
#         "constructionCostPerSqm": 1900.0,
#         "parkingCost": 1200.0,
#         "sharedAreasCost": 350.0,
#         "salesCommissionPct": 5.0,
#         "sellingPrice1": 25000.0,
#         "rentalPrice1": 850.0,
#         "landPrice": 9500.0,
#         "totalBuildings": 1.0,
#         "basementFloors": 2
#     }

    # print(comparison_result)
def start_comparison(project_1_data, project_2_data):
    # Compare the two
    comparison_result = compare_two_projects_as_json(project_1_data, project_2_data)

    return comparison_result
