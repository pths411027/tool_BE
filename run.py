import uvicorn
from app.main import app


if __name__ == '__main__':
    uvicorn.run(
        app='run:app', 
        host='0.0.0.0',
        port=8081, 
        reload=True,
    )