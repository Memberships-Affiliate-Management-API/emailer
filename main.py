from fastapi import FastAPI
import uvicorn

from typing import Optional
from datetime import datetime
from src.emailer import Emailer
from src.utils.utils import datetime_now

app = FastAPI()

emailer_instance: Emailer = Emailer()


@app.get("/")
async def root():
    return dict(message='root says hello')


@app.post("/send-mail")
async def send_email(email: str, subject: str, text: str, html: str, o_tag: Optional[str]) -> tuple:
    """main root of api"""
    _response = emailer_instance._send_with_mailgun_rest_api(to_list=[email], subject=subject, text=text, html=html,
                                                             o_tag=o_tag)
    return _response


@app.post("/schedule-mail")
async def schedule_mail(email: str, subject: str, text: str, html: str, o_tag: Optional[str],
                        time_scheduled: datetime, job_name: str):
    """
    **schedule_mail**
        schedules an email to be sent at a later date & time

        in order to check if the email was sent or not use the job_id and job_name to find out if the email was sent

    :param email: email address to send email to
    :param subject: subject of the email
    :param text: text formatted email body
    :param html: html formatted email body
    :param o_tag: email o:tag
    :param time_scheduled: time to send the email
    :param job_name: name of the email schedule
    :return: job_id, job_name, time_scheduled of the scheduled job
    """
    _kwargs: dict = dict(to_list=[email], subject=subject, text=text, html=html, o_tag=o_tag)
    _job_name: str = await emailer_instance._create_job_name(header_name=job_name)

    if datetime_now() > time_scheduled:
        _message: str = 'time scheduled has already passed'
        return dict(status=False, message=_message)

    _payload: dict = await emailer_instance._base_email_scheduler(func=emailer_instance._send_with_mailgun_rest_api,
                                                                  kwargs=_kwargs, job_name=_job_name,
                                                                  time_scheduled=time_scheduled)

    return dict(status=True, message='email scheduled', payload=_payload), 201

if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', port=8000)
