import asyncio

import pika
import json
from datetime import datetime
from main import emailer_instance


class EventProcessor:
    """
    **Class EventProcessor**
        depends on pika to provide a queue e of events to subscribe to

    **NOTE**

    by default event processor publishes two methods to api
        1. email-delivery-status
        2. email-scheduled

    by default event processor consumes the following methods
        1. send-email
        2. schedule-email
    """

    def __init__(self):
        self._valid_routing_targets = ['membership-api', 'system-admin-portal', 'client-admin-portal']
        self._queue_emailer: str = 'emailer'
        self._routing_target: str = 'membership-api'
        self.params = pika.URLParameters()
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self._queue_emailer)
        self.channel.basic_consume(queue=self._queue_emailer, on_message_callback=self.callback, auto_ack=True)
        print('started consuming')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.channel.close()

    def publish(self, method: str, body: dict):
        """
            **publish**
                will publish messages back to the api
        :return:
        """
        properties = pika.BasicProperties(method)
        self.channel.basic_publish(exchange='', routing_key=self._routing_target, body=json.dumps(body),
                                   properties=properties)

    def change_routing_target(self, target: str):
        """
        **change_routing_target**
            changes the target the event processor sends messages to
        :param target:
        :return:
        """
        self._routing_target = target if target in self._valid_routing_targets else 'membership-api'

    @staticmethod
    def get_email_fields(data: dict) -> tuple:
        """
            to_list: List[str],
            subject: str,
            text: str,
            html: str,
            o_tag: Optional[List[str]] = None
        :param data:
        :return:
        """
        email: str = data.get('email')
        subject: str = data.get('subject')
        text: str = data.get('text')
        html: str = data.get('html')
        o_tag: str = data.get('o_tag')
        job_name: str = data.get('job_name')
        time_scheduled: datetime = data.get('time_scheduled')
        return email, subject, text, html, o_tag, job_name, time_scheduled

    def callback(self, ch, method, properties, body):
        """
        **callback**
            called to process incoming messages sent to emailer

        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        data: dict = json.loads(body)
        if properties.content_type == "send-email":
            # call send email here
            email, subject, text, html, o_tag = self.get_email_fields(data=data)
            response = emailer_instance._send_with_mailgun_rest_api(to_list=[email], subject=subject, text=text,
                                                                    html=html, o_tag=o_tag)
        elif properties.content_type == "schedule-email":
            """
                
                @staticmethod 
                async def _base_email_scheduler(func: (...) -> Any,
                                                kwargs: dict,
                                                job_name: str = create_id(),
                                                time_scheduled: datetime = lambda time_scheduled:
                                                time_scheduled + datetime_now() + timedelta(seconds=10))
                  -> Coroutine[Any, Any, dict]
            """
            # call schedule email here
            email, subject, text, html, o_tag, job_name, time_scheduled = self.get_email_fields(data=data)
            _kwargs: dict = dict(to_list=[email], subject=subject, text=text, html=html, o_tag=o_tag)
            _job_name: str = await emailer_instance._create_job_name(header_name=job_name)

            response = asyncio.run(
                emailer_instance._base_email_scheduler(func=emailer_instance._send_with_mailgun_rest_api,
                                                       kwargs=_kwargs, job_name=_job_name,
                                                       time_scheduled=time_scheduled))
            self.publish(method='email-scheduled', body=response)
