from flask import Blueprint, render_template

manhinh_bp = Blueprint("manhinh", __name__)

acer_laptops_data = [
    {
        "Mẫu Laptop": "Acer Aspire 3 A315-58-32BG",
       
        "Kích thước màn hình": 15.6,
        "Độ phân giải màn hình": "FHD (1920x1080)",
        "Công nghệ màn hình": "IPS",

    },
    {
        "Mẫu Laptop": "Acer Aspire 5 A514-51-51XQ",
       
        "Kích thước màn hình": 14,
        "Độ phân giải màn hình": "FHD (1920x1080)",
        "Công nghệ màn hình": "IPS",

    },
    {
        "Mẫu Laptop": "Acer Swift 3 SF314-43 - R889",
     
        "Kích thước màn hình": 14,
        "Độ phân giải màn hình": "FHD (1920x1080)",
        "Công nghệ màn hình": "IPS",

    },
    {
        "Mẫu Laptop": "Acer Swift X SFX16-51G-516Q",
       
        "Kích thước màn hình": 16,
        "Độ phân giải màn hình": "FHD (1920x1080)",
        "Công nghệ màn hình": "IPS",

    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN515-57-52Y2",
      
        "Kích thước màn hình": 15.6,
        "Độ phân giải màn hình": "FHD (1920x1080)",
        "Công nghệ màn hình": "IPS 144Hz",

    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN517-54-79YT",
       
        "Kích thước màn hình": 17.3,
        "Độ phân giải màn hình": "FHD (1920x1080)",
        "Công nghệ màn hình": "IPS 144Hz",

    },
    {
        "Mẫu Laptop": "Acer Predator Helios 300 PH317-55-75QC",
       
        "Kích thước màn hình": 17.3,
        "Độ phân giải màn hình": "QHD (2560x1440)",
        "Công nghệ màn hình": "IPS 165Hz",

    },
    {
        "Mẫu Laptop": "Acer Predator Triton 300 SE PT314-52s-7169",
       
        "Kích thước màn hình": 14,
        "Độ phân giải màn hình": "WQXGA (2560x1600)",
        "Công nghệ màn hình": "IPS 165Hz",

    },
    {
        "Mẫu Laptop": "Acer TravelMate P1 TMP14-51-518K",
       
        "Kích thước màn hình": 14,
        "Độ phân giải màn hình": "FHD (1920x1080)",
        "Công nghệ màn hình": "IPS",

    },
    {
        "Mẫu Laptop": "Acer Chromebook Spin 713 CP713-3W-5102",
      
        "Kích thước màn hình": 13.5,
        "Độ phân giải màn hình": "2K (2256x1504)",
        "Công nghệ màn hình": "Cảm ứng",

    },
]


@manhinh_bp.route("/")
def manhinh_page():
    return render_template("manhinh.html", laptops=acer_laptops_data)
