from flask import Blueprint, render_template

chiphi_bp = Blueprint("chiphi", __name__)

acer_laptops_data = [
    {
        "Mẫu Laptop": "Acer Aspire 3 A315-58-32BG",
        "Giá (VNĐ)": 9990000,
    },
    {
        "Mẫu Laptop": "Acer Aspire 5 A514-51-51XQ",
       
        "Giá (VNĐ)": 14490000,
       
    },
    {
        "Mẫu Laptop": "Acer Swift 3 SF314-43 - R889",
      
        "Giá (VNĐ)": 17990000,
       
    },
    {
        "Mẫu Laptop": "Acer Swift X SFX16-51G-516Q",
     
        "Giá (VNĐ)": 24900000,
       
    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN515-57-52Y2",
      
        "Giá (VNĐ)": 22990000,
       
    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN517-54-79YT",
       
        "Giá (VNĐ)": 31990000,
      
    },
    {
        "Mẫu Laptop": "Acer Predator Helios 300 PH317-55-75QC",
       
        "Giá (VNĐ)": 48990000,
       
    },
    {
        "Mẫu Laptop": "Acer Predator Triton 300 SE PT314-52s-7169",
      
        "Giá (VNĐ)": 39990000,
      
    },
    {
        "Mẫu Laptop": "Acer TravelMate P1 TMP14-51-518K",
      
        "Giá (VNĐ)": 15990000,
       
    },
    {
        "Mẫu Laptop": "Acer Chromebook Spin 713 CP713-3W-5102",
      
        "Giá (VNĐ)": 18990000,
       
    },
]


@chiphi_bp.route("/")
def chiphi_page():
    return render_template("chiphi.html", laptops=acer_laptops_data)
