from flask import Blueprint, render_template

tgbh_bp = Blueprint("tgbh", __name__)

acer_laptops_data = [
    {
        "Mẫu Laptop": "Acer Aspire 3 A315-58-32BG",
       
        "Thời gian bảo hành": "12 tháng",
    },
    {
        "Mẫu Laptop": "Acer Aspire 5 A514-51-51XQ",
        "Thời gian bảo hành": "12 tháng",
    },
    {
        "Mẫu Laptop": "Acer Swift 3 SF314-43 - R889",
      
        "Thời gian bảo hành": "24 tháng",
    },
    {
        "Mẫu Laptop": "Acer Swift X SFX16-51G-516Q",
       
        "Thời gian bảo hành": "24 tháng",
    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN515-57-52Y2",
      
        "Thời gian bảo hành": "12 tháng",
    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN517-54-79YT",
       
        "Thời gian bảo hành": "12 tháng",
    },
    {
        "Mẫu Laptop": "Acer Predator Helios 300 PH317-55-75QC",
      
        "Thời gian bảo hành": "24 tháng",
    },
    {
        "Mẫu Laptop": "Acer Predator Triton 300 SE PT314-52s-7169",
       
        "Thời gian bảo hành": "24 tháng",
    },
    {
        "Mẫu Laptop": "Acer TravelMate P1 TMP14-51-518K",
       
        "Thời gian bảo hành": "12 tháng",
    },
    {
        "Mẫu Laptop": "Acer Chromebook Spin 713 CP713-3W-5102",
       
        "Thời gian bảo hành": "12 tháng",
    },
]


@tgbh_bp.route("/")
def tgbh_page():
    return render_template("tgbh.html", laptops=acer_laptops_data)
