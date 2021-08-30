dbConfig = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mirror',
    'port': 3306,
    'database': 'software',
}

allowed_documents = [
    'pdf', 'markdown', 'md', 'zip', 'rar', 'xlsx', 'txt',
    'ppt', 'pptx', 'xls', 'docx', 'doc'
                 ]
documents_path = "./statics/task/"
files_path = "./statics/file/"

SECRET_KEY = 'this_is_a_secret'
MaxTeam = 10
MaxPair = 2
