import os

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:kien170025436069@localhost/ahp_laptop_acer"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('ahptlaptopacersecretkeyhihihihahahahahohoohohhiaisdashawhhdashdasjdjasjd') or os.urandom(24)