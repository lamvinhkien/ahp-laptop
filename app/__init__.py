from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Đăng ký các Blueprints
    from app.routes.main import main_bp
    from app.routes.hieunang import hieunang_bp
    from app.routes.chiphi import chiphi_bp
    from app.routes.thietke import thietke_bp
    from app.routes.manhinh import manhinh_bp
    from app.routes.tlsd import tlsd_bp
    from app.routes.tgbh import tgbh_bp
    from app.routes.dungluong import dungluong_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(hieunang_bp, url_prefix="/hieu-nang")
    app.register_blueprint(chiphi_bp, url_prefix="/chi-phi")
    app.register_blueprint(thietke_bp, url_prefix="/thiet-ke")
    app.register_blueprint(manhinh_bp, url_prefix="/man-hinh")
    app.register_blueprint(tlsd_bp, url_prefix="/tlsd")
    app.register_blueprint(tgbh_bp, url_prefix="/tgbh")
    app.register_blueprint(dungluong_bp, url_prefix="/dung-luong")

    return app
