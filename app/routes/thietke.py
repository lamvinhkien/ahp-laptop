from flask import Blueprint, render_template

thietke_bp = Blueprint("thietke", __name__)

acer_laptops_data = [
    {
        "Mẫu Laptop": "Acer Aspire 3 A315-58-32BG",
       
        "Trọng lượng (Kg)": 1.7,
        "Độ mỏng": 19.9,
        "Chất liệu": "Nhựa",
    },
    {
        "Mẫu Laptop": "Acer Aspire 5 A514-51-51XQ",
      
        "Trọng lượng": 1.45,
        "Độ mỏng": 17.9,
        "Chất liệu": "Kim loại",
        
    },
    {
        "Mẫu Laptop": "Acer Swift 3 SF314-43 - R889",
       
        "Trọng lượng": 1.2,
        "Độ mỏng": 15.9,
        "Chất liệu": "Kim loại",
       
    },
    {
        "Mẫu Laptop": "Acer Swift X SFX16-51G-516Q",
       
        "Trọng lượng": 1.7,
        "Độ mỏng": 17.9,
        "Chất liệu": "Kim loại",
        
    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN515-57-52Y2",
      
        "Trọng lượng": 2.3,
        "Độ mỏng": 23.9,
        "Chất liệu": "Nhựa",
       
    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN517-54-79YT",
      
        "Trọng lượng": 2.7,
        "Độ mỏng": 24.9,
        "Chất liệu": "Nhựa",
       
    },
    {
        "Mẫu Laptop": "Acer Predator Helios 300 PH317-55-75QC",
       
        "Trọng lượng": 2.9,
        "Độ mỏng": 22.9,
        "Chất liệu": "Kim loại",
       
    },
    {
        "Mẫu Laptop": "Acer Predator Triton 300 SE PT314-52s-7169",
       
        "Trọng lượng": 1.7,
        "Độ mỏng": 17.9,
        "Chất liệu": "Kim loại",
        
    },
    {
        "Mẫu Laptop": "Acer TravelMate P1 TMP14-51-518K",
      
        "Trọng lượng": 1.6,
        "Độ mỏng": 17.9,
        "Chất liệu": "Kim loại",
       
    },
    {
        "Mẫu Laptop": "Acer Chromebook Spin 713 CP713-3W-5102",
      
        "Trọng lượng": 1.37,
        "Độ mỏng": 16.8,
        "Chất liệu": "Kim loại",
       
    },
]


@thietke_bp.route("/")
def thietke_page():
    return render_template("thietke.html", laptops=acer_laptops_data)
