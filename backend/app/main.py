from fastapi import FastAPI

app = FastAPI()

@app.get("/voltage") #what file thing its stored in ex: google.com/voltage
def get_voltage():
    print(3)
    return {"volts": 3, "amps": 100}
