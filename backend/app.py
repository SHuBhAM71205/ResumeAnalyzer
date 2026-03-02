from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def root():
    return {"Hello to the backend of the resume analyzer"}


