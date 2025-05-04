from flask import Blueprint, render_template, request, session
from app import db
from app.models import Criteria, Alternatives, AlternativeComparison, LaptopType
import numpy as np

main_bp = Blueprint("main", __name__)

preference_scale = {
    1 / 9: "1/9 - Ít quan trọng tuyệt đối hơn nhiều",
    1 / 8: "1/8 - Giữa 1/9 và 1/7",
    1 / 7: "1/7 - Ít quan trọng tuyệt đối",
    1 / 6: "1/6 - Giữa 1/7 và 1/5",
    1 / 5: "1/5 - Ít quan trọng hơn nhiều",
    1 / 4: "1/4 - Giữa 1/5 và 1/3",
    1 / 3: "1/3 - Ít quan trọng hơn",
    1 / 2: "1/2 - Ít quan trọng hơn một chút",
    1: "1 - Tương đương",
    2: "2 - Hơi quan trọng hơn",
    3: "3 - Quan trọng hơn",
    4: "4 - Rất quan trọng hơn",
    5: "5 - Cực kỳ quan trọng hơn",
    6: "6 - Giữa 5 và 7",
    7: "7 - Quan trọng tuyệt đối",
    8: "8 - Giữa 7 và 9",
    9: "9 - Quan trọng tuyệt đối hơn nhiều",
}

preference_options = sorted(preference_scale.keys())


def calculate_ahp_weights(comparison_matrix, criteria_names):
    n = comparison_matrix.shape[0]
    column_sums = comparison_matrix.sum(axis=0)
    normalized_matrix = comparison_matrix / column_sums
    weights = normalized_matrix.mean(axis=1)
    consistency_vector = np.dot(comparison_matrix, weights)
    lambda_max = np.mean(consistency_vector / weights)
    CI = (lambda_max - n) / (n - 1)
    RI_values = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    RI = RI_values.get(n, 0)
    CR = CI / RI if RI != 0 else 0
    return weights, CR


def generate_comparison_matrix_data(criteria, submitted_values=None, input_errors=None):
    n = len(criteria)
    comparison_matrix_data = [[None for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                comparison_matrix_data[i][j] = {"id": f"comparison_{criteria[i].id}_{criteria[j].id}", "criteria1": criteria[i].name, "criteria2": criteria[j].name, "value": "1", "readonly": True}
            elif i < j:
                comparison_id = f"comparison_{criteria[i].id}_{criteria[j].id}"
                submitted_value = submitted_values.get(comparison_id, "1") if submitted_values else "1"
                comparison_matrix_data[i][j] = {"id": comparison_id, "criteria1": criteria[i].name, "criteria2": criteria[j].name, "value": submitted_value, "readonly": False, 'error': input_errors.get(comparison_id) if input_errors else None}
            else:
                row_above = j
                col_above = i
                comparison_id_above = f"comparison_{criteria[row_above].id}_{criteria[col_above].id}"
                submitted_value_above = submitted_values.get(comparison_id_above, "1") if submitted_values else "1"
                try:
                    inverted_value = str(1 / eval(submitted_value_above)) if submitted_value_above and eval(submitted_value_above) != 0 else "1"
                except (ValueError, TypeError, ZeroDivisionError):
                    inverted_value = "1"
                comparison_matrix_data[i][j] = {"id": f"comparison_{criteria[i].id}_{criteria[j].id}", "criteria1": criteria[i].name, "criteria2": criteria[j].name, "value": inverted_value, "readonly": True}
    return comparison_matrix_data


@main_bp.route("/", methods=["GET", "POST"])
def home_page():
    criteria = Criteria.query.all()
    laptop_types = LaptopType.query.all()
    alternatives = []
    weights = session.get('weights')
    cr = session.get('cr')
    error = None
    submitted_values = session.get('criteria_comparison_values', {})
    input_errors = {}
    ranked_alternatives = []
    selected_laptop_type_id = request.form.get('selected_laptop_type_id') or session.get('selected_laptop_type_id')
    selected_laptop_type = LaptopType.query.get(selected_laptop_type_id) if selected_laptop_type_id else None

    criteria_names_list = [c.name for c in criteria]
    n = len(criteria)
    allowed_values_str = ["1/9", "1/8", "1/7", "1/6", "1/5", "1/4", "1/3", "1/2", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    if request.method == "POST":
        session['selected_laptop_type_id'] = request.form.get('selected_laptop_type_id')
        if not selected_laptop_type_id:
            error = "Vui lòng chọn loại laptop trước khi tính toán."
        else:
            selected_laptop_type = LaptopType.query.get(selected_laptop_type_id)
            alternatives = Alternatives.query.filter_by(laptop_type_id=selected_laptop_type_id).all()
            submitted_values_from_form = request.form.to_dict()
            session['criteria_comparison_values'] = submitted_values_from_form
            comparison_matrix = np.ones((n, n), dtype=float)
            valid_input = True

            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    comparison_id = f"comparison_{criteria[i].id}_{criteria[j].id}"
                    value_str = submitted_values_from_form.get(comparison_id, "1").strip()

                    if i < j:
                        if value_str and value_str not in allowed_values_str:
                            input_errors[comparison_id] = "Giá trị không hợp lệ. Chỉ chấp nhận: " + ", ".join(allowed_values_str)
                            valid_input = False
                            comparison_matrix[i, j] = 1.0
                            comparison_matrix[j, i] = 1.0
                        else:
                            try:
                                preference = float(eval(value_str)) if value_str else 1.0
                                comparison_matrix[i, j] = preference
                                comparison_matrix[j, i] = 1.0 / preference if preference != 0 else 0.00001
                            except (ValueError, TypeError, ZeroDivisionError):
                                input_errors[comparison_id] = "Lỗi giá trị."
                                valid_input = False
                                comparison_matrix[i, j] = 1.0
                                comparison_matrix[j, i] = 1.0

            if valid_input:
                weights_calculated, cr_calculated = calculate_ahp_weights(comparison_matrix, [c.name for c in criteria])
                weights = weights_calculated.tolist() if weights_calculated is not None else None
                cr = cr_calculated
                session['weights'] = weights
                session['cr'] = cr
                if cr >= 0.10:
                    error = "Tỷ số nhất quán (CR) vượt quá 10%. Vui lòng xem xét lại các đánh giá của bạn."

        comparison_matrix_data = generate_comparison_matrix_data(criteria, submitted_values_from_form, input_errors)

    else:
        comparison_matrix_data = generate_comparison_matrix_data(criteria, session.get('criteria_comparison_values'))

    return render_template(
        "home.html",
        comparison_matrix=comparison_matrix_data,
        criteria_names=criteria_names_list,
        allowed_values=allowed_values_str,
        weights=weights,
        cr=cr,
        error=error,
        ranked_alternatives=ranked_alternatives,
        laptop_types=laptop_types,
        selected_laptop_type=selected_laptop_type,
    )