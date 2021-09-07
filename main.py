from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from typing import Optional
from datetime import datetime

from src.utils.utils import datetime_now

from src.events.events import EventProcessor

events_instance: EventProcessor = EventProcessor()

from src.emailer import Emailer

emailer_instance: Emailer = Emailer()

app = FastAPI()


class EmailModel(BaseModel):
    email: str
    subject: str
    text: str
    html: str
    o_tag: Optional[str]


class EmailSchedulerModel(EmailModel):
    time_scheduled: datetime
    job_name: str


@app.get("/")
async def root():
    return dict(message='root says hello')


@app.post("/send-mail")
async def send_email(email_data: EmailModel) -> tuple:
    """
    **send_email**
        this end-points sends an email to a target recipients given only email, subject, text, html and o_tag

    :param email_data: email data_type
    :return:
    """
    _response = emailer_instance._send_with_mailgun_rest_api(to_list=[email_data.email], subject=email_data.subject,
                                                             text=email_data.text, html=email_data.html,
                                                             o_tag=email_data.o_tag)
    data, status_code = _response
    return dict(status=True, message='email was successfully sent', payload=data), status_code


@app.post("/schedule-mail")
async def schedule_mail(schedule_data: EmailSchedulerModel):
    """
    **schedule_mail**
        schedules an email to be sent at a later date & time

        in order to check if the email was sent or not use the job_id and job_name to find out if the email was sent

    :param schedule_data:
    :return: job_id, job_name, time_scheduled of the scheduled job
    """
    _kwargs: dict = dict(to_list=[schedule_data.email], subject=schedule_data.subject, text=schedule_data.text,
                         html=schedule_data.html, o_tag=schedule_data.o_tag)
    _job_name: str = emailer_instance._create_job_name(header_name=schedule_data.job_name)

    if datetime_now() > schedule_data.time_scheduled:
        _message: str = 'time scheduled has already passed'
        return dict(status=False, message=_message)

    _payload: dict = await emailer_instance._base_email_scheduler(func=emailer_instance._send_with_mailgun_rest_api,
                                                                  kwargs=_kwargs, job_name=_job_name,
                                                                  time_scheduled=schedule_data.time_scheduled)

    return dict(status=True, message='email scheduled', payload=_payload), 201


if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', port=8000)
