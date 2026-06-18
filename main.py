from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, World!"}