"""
    **Mailgun Emails Integration SDK**
        *Python ^3.8
        class to send emails through a mailgun rest api
        # You can see a record of this email in your logs: https://app.mailgun.com/app/logs.
        # You can send up to 300 emails/day from this sandbox server.
        # Next, you should add your own domain so you can send 10000 emails/month for free.

"""
__developer__ = "mobius-crypt"
__email__ = "mobiusndou@gmail.com"
__twitter__ = "@blueitserver"
__github_repo__ = "https://github.com/freelancing-solutions/memberships-and-affiliate-api"
__github_profile__ = "https://github.com/freelancing-solutions/"

from datetime import timedelta, datetime
from src.schedulers.scheduler import task_scheduler
from config import config_instance
from typing import List, Optional, Callable, Coroutine
import aiohttp
import asyncio

from main import events_instance

from src.utils.utils import datetime_now, create_id


class Emailer:
    """
        **Class Emailer**
            methods to integrate Mailgun Emailing rest API with Memberships & Affiliates APIKeys
            for the purposes of sending notifications and emails on behalf of clients.

        TODO - feature development add Mailgun Templates see Email-templates on Github Repos
    """

    def __init__(self) -> None:
        """
            mailgun_domain : domain name registered with mailgun
            MAILGUN_API_KEY : can be found from mailgun control panel
        """
        self._base_url: str = config_instance.BASE_URL
        self._mailgun_api_key = config_instance.MAILGUN_API_KEY
        self._mailgun_end_point = "https://api.mailgun.net/v3/{}/messages".format(config_instance.MAILGUN_DOMAIN)
        self._mailgun_no_response_email = config_instance.MAILGUN_NO_RESPONSE
        self._secret_key: str = config_instance.SECRET_KEY

    @staticmethod
    async def _async_request(_url, json_data, headers, auth) -> tuple:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=_url, auth=auth, json=json_data, headers=headers) as response:
                json_data: dict = await response.json()
                return json_data, response.status

    def _send_with_mailgun_rest_api(self, to_list: List[str], subject: str, text: str, html: str,
                                    o_tag: List[str] = None) -> tuple:
        """
        **_send_with_mailgun_rest_api**
            a method to send email via rest api

        :param o_tag:  message o tag | format of o:tag  ["September newsletter", "newsletters"]
        :param to_list: list of email addresses to send this email format ["bar@example.com", "YOU@YOUR_DOMAIN_NAME"]
        :param subject: the subject of the email
        :param text: the text part of the email
        :param html: the html part of the email
        :return: bool
        """
        # NOTE: from mail must be registered with MAILGUN
        from_str: str = f'{config_instance.APP_NAME} <{self._mailgun_no_response_email}>'
        to_str: List[str] = to_list

        _auth: tuple = ("api", f"{self._mailgun_api_key}")
        data: dict = {"from": from_str, "to": to_str, "subject": subject, "text": text, "html": html, 'o:tag': o_tag}

        _headers: dict = {'content-type': 'application/json'}
        response = asyncio.run(self._async_request(_url=self._mailgun_end_point, json_data=data, headers=_headers,
                                                   auth=_auth))

        data, status_code = response
        data.update(status_code=status_code)

        events_instance.publish(method='email-delivery-status', body=data)
        return data, status_code

    @staticmethod
    async def _base_email_scheduler(func: Callable, kwargs: dict, job_name: str = create_id(),
                                    time_scheduled: datetime = lambda time_scheduled:
                                    time_scheduled + datetime_now() + timedelta(seconds=10)) -> dict:
        """

        :param func:
        :param kwargs:
        :return: None
        """
        if not isinstance(time_scheduled, datetime):
            time_scheduled: datetime = datetime_now() + timedelta(seconds=10)
        _job_id: str = create_id()

        task_scheduler.add_job(func=func, trigger='date', run_date=time_scheduled, kwargs=kwargs, id=_job_id,
                               name=job_name, misfire_grace_time=360)

        return dict(job_id=_job_id, job_name=job_name, time_scheduled=time_scheduled)

    @staticmethod
    async def _create_job_name(header_name: str) -> str: return f'{header_name}{create_id()[0:20]}'


