import time

BASE_URL = "https://id.indeed.com/jobs?q=python&l=bandung"
INCLUDE_KEYWORDS = ["python", "selenium", "microcontroller",
                    "arduino", "stm32", "esp32", "sensor", "iot", "excel", "sql", "analyst", "trainee"]
EXCLUDE_KEYWORDS = ["fullstack", "android", "ios", "flutter", "fiber"]
FILE_OUT = f'result_Indeed-{time.ctime().replace(":","-")}.csv'
