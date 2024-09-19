from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
from pytz import timezone
import pandas as pd
import pymysql.cursors

app = FastAPI()

origins = [
    "http://localhost:8899", # 로컬
    "https://samdul97food-b2b1c.web.app", # 맨 끝에 / 있으면 안돌아감!!!!
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "n97"}

@app.get("/food")
def food(name: str):
    # 현재 이곳에 들어오는 시간
    ts = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

    # 음식 이름과 시간을 csv 형태로 저장 -> 경로 : ~/code/data/food.csv
    path = os.getenv("FILE_PATH", f"{os.getenv('HOME')}/tmp/foodcsv/food.csv")
    if os.path.exists(path): # 파일이 이미 있다면
        data = pd.read_csv(path)
        df = pd.DataFrame({'time' : [ts], 'food' : [name]})
        new_df = pd.concat([data, df], ignore_index = True)
        new_df.to_csv(path, index = False)
    else: # 없다면
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df = pd.DataFrame({'time' : [ts], 'food' : [name]})
        df.to_csv(path, index = False)

    # DB insert
    connection = pymysql.connect(host=os.getenv("DB_IP", "localhost"),
                             user='food',
                             password='1234',
                             database='fooddb',
                             port=int(os.getenv("MY_PORT", 33306)),
                             cursorclass=pymysql.cursors.DictCursor)
    sql = "INSERT INTO `foodhistory`(username, foodname, dt) VALUES (%s, %s, %s)"
    with connection:
        with connection.cursor() as cursor:
            # sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
            # cursor.execute(sql, ('webmaster@python.org',))
            cursor.execute(sql,("n97",name,ts))
        connection.commit()

    return {'time' : ts, 'food' : name} # return값은 아무렇게나 해도 됨
