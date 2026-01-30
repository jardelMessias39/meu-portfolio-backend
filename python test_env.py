
import os

mongo_url = os.getenv('MONGO_URL')
db_name = os.getenv('DB_NAME')
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    raise Exception("OPENAI_API_KEY não está definida no ambiente")
else:
    print("OPENAI_API_KEY está definida")