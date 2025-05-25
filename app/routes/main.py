import os
from io import BytesIO
from flask import Blueprint, render_template, request, session, send_file
from app import db
from app.models import Criteria, Alternatives, AlternativeComparison, LaptopType
import numpy as np
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer, SimpleDocTemplate
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from flask import session, send_file
from datetime import datetime

main_bp = Blueprint("main", __name__)

# Đường dẫn đến thư mục result
RESULT_FOLDER = os.path.join(os.getcwd(), 'result')
os.makedirs(RESULT_FOLDER, exist_ok=True) # Đảm bảo thư mục tồn tại

font_path = os.path.join(os.getcwd(), 'fonts', 'Roboto-Regular.ttf')
pdfmetrics.registerFont(TTFont('Roboto', font_path))

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

# Hàm mới để chuyển đổi tên tiêu chí
def get_abbreviated_criteria_name(name):
    if name == "Thời gian bảo hành":
        return "TGBH"
    if name == "Thời lượng sử dụng":
        return "TLSD"
    return name

# Hàm mới để lấy giá trị hiển thị từ giá trị số (ví dụ: 0.111 -> "1/9")
def get_display_value_from_numeric(numeric_val):
    # Sử dụng tolerance cho so sánh số thực
    tolerance = 1e-6
    for key_val, display_str_full in preference_scale.items():
        if np.isclose(numeric_val, key_val, atol=tolerance):
            # Trích xuất phần số/phân số từ chuỗi đầy đủ (ví dụ: "1/9 - ..." -> "1/9")
            return display_str_full.split(' - ')[0]
    # Nếu không khớp với giá trị nào trong scale, làm tròn và trả về dưới dạng chuỗi
    # Điều này xảy ra nếu có lỗi tính toán hoặc giá trị không thuộc thang AHP chuẩn
    return f"{numeric_val:.3f}" # Làm tròn đến 3 chữ số thập phân nếu không có dạng phân số

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
    ranked_alternatives = session.get('ranked_alternatives', []) # Lấy từ session
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


@main_bp.route('/update_session', methods=['POST'])
def update_session():
    data = request.get_json()
    session['ranked_alternatives'] = data.get('ranked_alternatives', [])
    return '', 204 # Trả về No Content


@main_bp.route("/export_pdf")
def export_pdf():
    selected_laptop_type_id = session.get('selected_laptop_type_id')
    selected_laptop_type = LaptopType.query.get(selected_laptop_type_id)
    criteria = Criteria.query.all()
    criteria_names = [c.name for c in criteria]
    weights = session.get('weights')
    comparison_values = session.get('criteria_comparison_values', {})
    ranked_alternatives_data = session.get('ranked_alternatives', [])  # Lấy dữ liệu xếp hạng từ session

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"ket_qua_ahp_{timestamp}.pdf"
    pdf_path = os.path.join(RESULT_FOLDER, pdf_filename)

    # Đăng ký font Roboto từ file đã tải
    font_path = os.path.join(os.getcwd(), 'fonts', 'Roboto-Regular.ttf')
    pdfmetrics.registerFont(TTFont('Roboto', font_path))

    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            rightMargin=2 * cm, leftMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)

    styles = getSampleStyleSheet()
    # Gán font Roboto cho tất cả các style mặc định
    for style_name in styles.byName:
        styles[style_name].fontName = 'Roboto'

    story = []

    # Tiêu đề
    story.append(Paragraph("<b>Kết quả phân tích lựa chọn Laptop Acer</b>", styles['Title']))
    story.append(Spacer(1, 12))

    # Loại laptop đã chọn
    if selected_laptop_type:
        story.append(Paragraph(f"<b>Loại laptop đã chọn:</b> {selected_laptop_type.name}", styles['Heading2']))

    # Bảng ma trận so sánh cặp tiêu chí
    story.append(Paragraph("<b>Ma trận so sánh cặp tiêu chí</b>", styles['Heading2']))

    # Áp dụng hàm chuyển đổi tên tiêu chí cho tiêu đề cột
    abbreviated_criteria_names = [get_abbreviated_criteria_name(name) for name in criteria_names]
    comparison_data = [[""] + abbreviated_criteria_names]

    n = len(criteria)
    for i in range(n):
    # Áp dụng hàm chuyển đổi tên tiêu chí cho tiêu đề hàng
        row = [get_abbreviated_criteria_name(criteria_names[i])]
        for j in range(n):
            if i == j:
                value = "1"
            elif i < j:
                comparison_id = f"comparison_{criteria[i].id}_{criteria[j].id}"
                value = comparison_values.get(comparison_id, "1")
            else: # i > j, ô nghịch đảo
                comparison_id_above = f"comparison_{criteria[j].id}_{criteria[i].id}"
                submitted_value_above = comparison_values.get(comparison_id_above, "1")
                try:
                    # Chuyển đổi chuỗi nhập liệu thành số thực
                    val = eval(submitted_value_above)
                    # Đảm bảo không chia cho 0. Nếu val là 0, đặt là 0.0 để tránh lỗi và xử lý tiếp.
                    inverted_value_numeric = 1 / val if val != 0 else 0.0
                    # Sử dụng hàm mới để lấy giá trị hiển thị dạng phân số/số nguyên
                    value = get_display_value_from_numeric(inverted_value_numeric)
                except (ValueError, TypeError, ZeroDivisionError, SyntaxError):
                    # Nếu có lỗi khi eval hoặc tính toán, đặt giá trị mặc định là "1"
                    value = "1"
            row.append(value)
        comparison_data.append(row)

    table = Table(comparison_data, colWidths=[3 * cm] + [2 * cm] * n)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    # Trọng số tiêu chí
    if weights:
        story.append(Paragraph("<b>Trọng số tiêu chí</b>", styles['Heading2']))
        weights_data = [["Tiêu chí", "Trọng số"]]
        for i, weight in enumerate(weights):
            # Chuyển đổi trọng số sang % và làm tròn 2 chữ số thập phân
            weights_data.append([criteria_names[i], f"{weight * 100:.2f}%"]) # Thay đổi ở đây
        weight_table = Table(weights_data, colWidths=[8 * cm, 3 * cm])
        weight_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(weight_table)
        story.append(Spacer(1, 12))

    # CR
    cr = session.get('cr')
    if cr is not None:
        # Chuyển đổi CR sang % và làm tròn 2 chữ số thập phân
        story.append(Paragraph(f"<b>Tỷ số nhất quán CR:</b> {cr * 100:.2f}%", styles['Normal'])) # Thay đổi ở đây

    # Xếp hạng các lựa chọn
    if ranked_alternatives_data:
        story.append(Paragraph("<b>Danh sách xếp hạng các lựa chọn</b>", styles['Heading2']))

        # Style cho tên lựa chọn
        wrap_style = ParagraphStyle(
            name='WrapStyle',
            fontName='Roboto', # Giữ nguyên Roboto
            fontSize=10,
            leading=12,
            wordWrap='CJK',
        )

        ranked_data = [["STT", "Tên lựa chọn", "Điểm số"]]
        for idx, item in enumerate(ranked_alternatives_data, 1):
            alternative_name = item.get('alternative', '')
            name_paragraph = Paragraph(alternative_name, wrap_style)
            # Chuyển đổi điểm số sang % và làm tròn 2 chữ số thập phân
            ranked_data.append([str(idx), name_paragraph, f"{item.get('score', 0) * 100:.2f}%"]) # Thay đổi ở đây

        ranked_table = Table(ranked_data, colWidths=[2 * cm, 11 * cm, 3 * cm])
        ranked_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'), # Bạn có thể muốn ALIGN LEFT cho cột tên lựa chọn
            ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(ranked_table)

    doc.build(story)

    return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
