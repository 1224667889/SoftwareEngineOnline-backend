"""主函数"""
from app import create_app


app = create_app(debug=False)
if __name__ == '__main__':
    app.run(port=8080)
