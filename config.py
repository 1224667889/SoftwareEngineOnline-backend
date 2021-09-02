dbConfig = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mirror',
    'port': 3306,
    'database': 'software',
}

mongoConfig = {
    "host": "124.71.105.78",
    "port": "8500"
}

spider_url = "http://172.17.173.97:8001/api/task/add"
spider_token = "abaa3286-7877-523c-8fd1-105332c7e991"

allowed_documents = [
    'pdf', 'markdown', 'md', 'zip', 'rar', 'xlsx', 'txt',
    'ppt', 'pptx', 'xls', 'docx', 'doc'
                 ]
documents_path = "./statics/task/"
files_path = "./statics/file/"

SECRET_KEY = 'this_is_a_secret'
MaxTeam = 10
MaxPair = 2
