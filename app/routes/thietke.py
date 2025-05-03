from flask import Blueprint, render_template, request, session, jsonify
from app import db
from app.models import Alternatives, AlternativeComparison, LaptopType, Criteria
import numpy as np

thietke_bp = Blueprint("thietke", __name__, url_prefix="/thiet-ke")

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

def calculate_ahp_weights(comparison_matrix, alternative_names):
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

def get_suggested_preference(alt1_id, alt2_id, criteria_id, laptop_type_id):
    comparison = AlternativeComparison.query.filter(
        (AlternativeComparison.alternative1_id == alt1_id) & (AlternativeComparison.alternative2_id == alt2_id) & (AlternativeComparison.criteria_id == criteria_id) & (AlternativeComparison.laptop_type_id == laptop_type_id)
    ).first()
    if comparison:
        return comparison.preference_value
    comparison_reversed = AlternativeComparison.query.filter(
        (AlternativeComparison.alternative1_id == alt2_id) & (AlternativeComparison.alternative2_id == alt1_id) & (AlternativeComparison.criteria_id == criteria_id) & (AlternativeComparison.laptop_type_id == laptop_type_id)
    ).first()
    if comparison_reversed and comparison_reversed.preference_value != 0:
        return 1 / comparison_reversed.preference_value
    return 1.0

def float_to_ahp_scale(value, tolerance=1e-6):
    conversion_map = {
        1/9: "1/9", 1/8: "1/8", 1/7: "1/7", 1/6: "1/6", 1/5: "1/5", 1/4: "1/4", 1/3: "1/3", 1/2: "1/2",
        1.0: "1", 2.0: "2", 3.0: "3", 4.0: "4", 5.0: "5", 6.0: "6", 7.0: "7", 8.0: "8", 9.0: "9",
    }

    if value in conversion_map:
        return conversion_map[value]
    elif abs(value - 1/3) < tolerance:
        return "1/3"
    elif abs(value - 2/3) < tolerance:
        return "2/3"
    elif abs(value - 1/9) < tolerance:
        return "1/9"
    elif abs(value - 1/7) < tolerance:
        return "1/7"
    elif abs(value - 1/5) < tolerance:
        return "1/5"
    elif abs(value - 1/2) < tolerance:
        return "1/2"
    elif abs(value - 1/4) < tolerance:
        return "1/4"
    elif abs(value - 1/6) < tolerance:
        return "1/6"
    elif abs(value - 1/8) < tolerance:
        return "1/8"
    elif abs(value - 1.0) < tolerance and 1.0 in conversion_map:
        return conversion_map[1.0]
    elif abs(value - 2.0) < tolerance and 2.0 in conversion_map:
        return conversion_map[2.0]
    elif abs(value - 3.0) < tolerance and 3.0 in conversion_map:
        return conversion_map[3.0]
    elif abs(value - 4.0) < tolerance and 4.0 in conversion_map:
        return conversion_map[4.0]
    elif abs(value - 5.0) < tolerance and 5.0 in conversion_map:
        return conversion_map[5.0]
    elif abs(value - 6.0) < tolerance and 6.0 in conversion_map:
        return conversion_map[6.0]
    elif abs(value - 7.0) < tolerance and 7.0 in conversion_map:
        return conversion_map[7.0]
    elif abs(value - 8.0) < tolerance and 8.0 in conversion_map:
        return conversion_map[8.0]
    elif abs(value - 9.0) < tolerance and 9.0 in conversion_map:
        return conversion_map[9.0]
    else:
        return f"{value:.4g}"

def generate_alternative_comparison_matrix_data(alternatives, criteria_id, laptop_type_id, load_suggestions=False, submitted_values=None, input_errors=None):
    n = len(alternatives)
    comparison_matrix_data = [[None for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            alt1 = alternatives[i]
            alt2 = alternatives[j]
            comparison_id = f"comparison_{alt1.id}_{alt2.id}"
            suggested_value_float = get_suggested_preference(alt1.id, alt2.id, criteria_id, laptop_type_id)

            default_value = "1"
            current_value = submitted_values.get(comparison_id, default_value) if submitted_values else default_value
            error = input_errors.get(comparison_id) if input_errors else None

            if i == j:
                comparison_matrix_data[i][j] = {"id": comparison_id, "alternative1": alt1.name, "alternative2": alt2.name, "value": "1", "readonly": True}
            elif i < j:
                value_to_display = current_value
                if load_suggestions and suggested_value_float is not None:
                    value_to_display = float_to_ahp_scale(suggested_value_float)
                comparison_matrix_data[i][j] = {"id": comparison_id, "alternative1": alt1.name, "alternative2": alt2.name, "value": value_to_display, "readonly": False, 'error': error}
            else:
                # Lấy giá trị nghịch đảo từ submitted_values nếu có
                corresponding_upper_id = f"comparison_{alt2.id}_{alt1.id}"
                submitted_upper_value_str = submitted_values.get(corresponding_upper_id) if submitted_values else None
                value_to_display = "1"  # Giá trị mặc định

                if submitted_upper_value_str:
                    try:
                        upper_value = float(eval(submitted_upper_value_str)) if submitted_upper_value_str else 1.0
                        if upper_value != 0:
                            value_to_display = f"{1/upper_value:.4g}"
                        else:
                            value_to_display = "0.0001"  # Tránh chia cho 0
                    except (ValueError, TypeError, ZeroDivisionError):
                        value_to_display = "1"  # Xử lý lỗi chuyển đổi

                # Nếu không có giá trị submitted (hoặc lỗi) và đang load gợi ý
                elif load_suggestions and suggested_value_float is not None and suggested_value_float != 0:
                    value_to_display = f"{1/suggested_value_float:.4g}"

                comparison_matrix_data[i][j] = {"id": comparison_id, "alternative1": alt1.name, "alternative2": alt2.name, "value": value_to_display, "readonly": True}

    return comparison_matrix_data

@thietke_bp.route("/", methods=["GET", "POST"])
def thietke_page():
    criteria_name = "Thiết kế"
    criteria = Criteria.query.filter_by(name=criteria_name).first()
    laptop_types = LaptopType.query.all()
    selected_laptop_type_id = request.form.get('selected_laptop_type_id') or request.args.get('selected_laptop_type_id') or session.get('thietke_selected_laptop_type_id')
    selected_laptop_type = LaptopType.query.get(selected_laptop_type_id)
    alternatives = []
    if selected_laptop_type_id:
        session['thietke_selected_laptop_type_id'] = selected_laptop_type_id
        alternatives = Alternatives.query.filter_by(laptop_type_id=selected_laptop_type_id).all()

    weights = session.get('thietke_weights')
    cr = session.get('thietke_cr')
    error = None
    submitted_values = session.get('thietke_comparison_values', {})
    input_errors = {}
    alternative_names = [alt.name for alt in alternatives]
    n = len(alternatives)
    allowed_values_str = ["1/9", "1/8", "1/7", "1/6", "1/5", "1/4", "1/3", "1/2", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    if not criteria:
        error = f"Không tìm thấy tiêu chí '{criteria_name}'."

    load_suggestions = request.form.get('load_suggestions') == 'true'

    if request.method == "POST" and criteria and selected_laptop_type:
        submitted_values_from_form = request.form.to_dict()
        session['thietke_comparison_values'] = submitted_values_from_form
        comparison_matrix = np.ones((n, n), dtype=float)
        valid_input = True

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                alt1 = alternatives[i]
                alt2 = alternatives[j]
                comparison_id = f"comparison_{alt1.id}_{alt2.id}"
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
            weights_calculated, cr_calculated = calculate_ahp_weights(comparison_matrix, alternative_names)
            weights = weights_calculated.tolist() if weights_calculated is not None else None
            cr = cr_calculated
            session['thietke_weights'] = weights
            session['thietke_cr'] = cr
            session['alternative_weights'] = session.get('alternative_weights', {})
            if weights:
                session['alternative_weights']['thietke'] = dict(zip(alternative_names, weights))
            else:
                if 'thietke' in session['alternative_weights']:
                    del session['alternative_weights']['thietke']

            if cr >= 0.10:
                error = "Tỷ số nhất quán (CR) vượt quá 10%. Vui lòng xem xét lại các đánh giá của bạn."
        else:
            error = "Vui lòng sửa các lỗi nhập liệu."

        comparison_matrix_data = generate_alternative_comparison_matrix_data(alternatives, criteria.id, selected_laptop_type_id, load_suggestions, submitted_values_from_form, input_errors)

    elif criteria and selected_laptop_type_id:
        comparison_matrix_data = generate_alternative_comparison_matrix_data(alternatives, criteria.id, selected_laptop_type_id, load_suggestions, session.get('thietke_comparison_values'))
    else:
        comparison_matrix_data = generate_alternative_comparison_matrix_data(alternatives, 0, 0) # Placeholder if no laptop type selected

    ranked_alternative_weights = []
    if weights:
        ranked_alternative_weights = sorted(zip(alternative_names, weights), key=lambda x: x[1], reverse=True)

    return render_template(
        "thietke.html",
        comparison_matrix=comparison_matrix_data,
        alternative_names=alternative_names,
        allowed_values=allowed_values_str,
        weights=weights,
        cr=cr,
        error=error,
        ranked_alternative_weights=ranked_alternative_weights,
        selected_laptop_type=selected_laptop_type,
        criteria_name=criteria_name,
        laptop_types=laptop_types,
        current_laptop_type_id=selected_laptop_type_id
    )