# main.py: my entry point to run the app
import uvicorn  # importing uvicorn to serve the fastapi app

if __name__ == "__main__":  # checking if we're running this file directly
    uvicorn.run(app="app.app:app",host="0.0.0.0",port=8000,reload=True)  # starting the server on port 8000 and turning on reload so it updates when I save
