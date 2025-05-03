from flask import Blueprint, render_template

dungluong_bp = Blueprint("dungluong", __name__)

acer_laptops_data = [
    {
        "Mẫu Laptop": "Acer Aspire 3 A315-58-32BG",
      
        "Dung lượng lưu trữ": "512GB SSD",
    },
    {
        "Mẫu Laptop": "Acer Aspire 5 A514-51-51XQ",
      
        "Dung lượng lưu trữ": "512GB SSD",
    },
    {
        "Mẫu Laptop": "Acer Swift 3 SF314-43 - R889",
       
        "Dung lượng lưu trữ": "512GB SSD",
    },
    {
        "Mẫu Laptop": "Acer Swift X SFX16-51G-516Q",
       
        "Dung lượng lưu trữ": "512GB SSD",
    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN515-57-52Y2",
       
        "Dung lượng lưu trữ": "512GB SSD",
    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN517-54-79YT",
       
        "Dung lượng lưu trữ": "512GB SSD",
    },
    {
        "Mẫu Laptop": "Acer Predator Helios 300 PH317-55-75QC",
     
        "Dung lượng lưu trữ": "1TB SSD",
    },
    {
        "Mẫu Laptop": "Acer Predator Triton 300 SE PT314-52s-7169",
       
        "Dung lượng lưu trữ": "1TB SSD",
    },
    {
        "Mẫu Laptop": "Acer TravelMate P1 TMP14-51-518K",
      
        "Dung lượng lưu trữ": "256GB SSD",
    },
    {
        "Mẫu Laptop": "Acer Chromebook Spin 713 CP713-3W-5102",
       
        "Dung lượng lưu trữ": "256GB SSD",
    },
]


@dungluong_bp.route("/")
def dungluong_page():
    return render_template("dungluong.html", laptops=acer_laptops_data)
