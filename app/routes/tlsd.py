from flask import Blueprint, render_template

tlsd_bp = Blueprint("tlsd", __name__)

acer_laptops_data = [
    {
        "Mẫu Laptop": "Acer Aspire 3 A315-58-32BG",
      
        "Pin (Giờ)": 9.9,

    },
    {
        "Mẫu Laptop": "Acer Aspire 5 A514-51-51XQ",
      
        "Pin (Giờ)": 7.9,

    },
    {
        "Mẫu Laptop": "Acer Swift 3 SF314-43 - R889",
     
        "Pin (Giờ)": 15.9,

    },
    {
        "Mẫu Laptop": "Acer Swift X SFX16-51G-516Q",
      
        "Pin (Giờ)": 17.9,

    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN515-57-52Y2",
      
        "Pin (Giờ)": 6,

    },
    {
        "Mẫu Laptop": "Acer Nitro 5 AN517-54-79YT",
      
        "Pin (Giờ)": 5,

    },
    {
        "Mẫu Laptop": "Acer Predator Helios 300 PH317-55-75QC",
       
        "Pin (Giờ)": 2.9,

    },
    {
        "Mẫu Laptop": "Acer Predator Triton 300 SE PT314-52s-7169",
      
        "Pin (Giờ)": 9,

    },
    {
        "Mẫu Laptop": "Acer TravelMate P1 TMP14-51-518K",
      
        "Pin (Giờ)": 12,

    },
    {
        "Mẫu Laptop": "Acer Chromebook Spin 713 CP713-3W-5102",
        "Pin (Giờ)": 10,

    },
]


@tlsd_bp.route("/")
def tlsd_page():
    return render_template("tlsd.html", laptops=acer_laptops_data)
