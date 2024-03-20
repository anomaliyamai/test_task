from datetime import datetime
from http import HTTPStatus
import uvicorn
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
import os


class Deposit(BaseModel):
    date: str = Field(pattern=r'^\d{2}\.\d{2}\.\d{4}$')
    periods: int = Field(ge=1, le=60)
    amount: int = Field(ge=10000, le=3000000)
    rate: float = Field(ge=1, le=8)


def check_correctness_of_date(provided_date: str) -> datetime | None:
    try:
        date_to_return = datetime.strptime(provided_date, "%d.%m.%Y")
    except ValueError:
        return
    return date_to_return


def deposit_algorithm(start_date: datetime, periods: int, amount: int, rate: float) -> dict:
    deposit_calendar = dict()
    for number_of_month in range(1, periods + 1):
        amount = amount + amount * (rate / 100) / 12
        deposit_calendar[(start_date + relativedelta(months=number_of_month)).strftime("%d.%m.%Y")] = amount
    return deposit_calendar


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    error_message = ""
    if len(exception.errors()[0]['loc']) < 2:
        error_message = "Problem occurred with body. Missing body."
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST.value,
                            content={"error": error_message})
    flag_for_date = False
    for error_number in range(len(exception.errors())):
        if error_number == len(exception.errors()) - 1:
            error_message += ('Problem occurred with json field ' + exception.errors()[error_number]['loc'][1]
                              + ': ' + exception.errors()[error_number]['msg'])
        else:
            error_message += ('Problem occurred with json field ' + exception.errors()[error_number]['loc'][1]
                              + ': ' + exception.errors()[error_number]['msg'] + ". ")
        if exception.errors()[error_number]['loc'][1] == "date":
            flag_for_date = True
    if not flag_for_date:
        data = await request.json()
        if 'date' in data.keys() and type(check_correctness_of_date(data['date'])) == JSONResponse:
            error_message += ". Problem occurred with json field date: Date cannot exist."
    return JSONResponse(status_code=HTTPStatus.BAD_REQUEST.value,
                        content={"error": error_message})


@app.post("/calculate")
async def calculate(deposit_data: Deposit):
    parsed_date = check_correctness_of_date(deposit_data.date)
    if not parsed_date:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST.value,
                            content={"error": "Problem occurred with json field date: Date cannot exist."})
    resulting_deposit_calendar = deposit_algorithm(check_correctness_of_date(deposit_data.date),
                                                   deposit_data.periods, deposit_data.amount, deposit_data.rate)
    return resulting_deposit_calendar


if __name__ == "__main__":
    uvicorn.run(
        'app:app',
        host=os.environ.get("HOST"),
        port=int(os.environ.get("PORT")),
        reload=True
    )
