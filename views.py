from main import app

@app.route('/')
def index():
    return {"message": "Hello, World!"}