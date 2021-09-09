import asyncio
import pika
import json
from datetime import datetime
from pika.adapters.blocking_connection import BlockingChannel
from src.config import config_instance


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

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
    """

    def __init__(self):
        self._valid_routing_targets = ['membership-api', 'system-admin-portal', 'client-admin-portal']
        self._queue_emailer: str = 'emailer'
        self._routing_target: str = 'membership-api'

        self.connection = pika.BlockingConnection(pika.URLParameters(url=config_instance.RABBIT_MQ_URL))
        self.consume_channel = self.connection.channel()
        self.consume_channel.queue_declare(queue=self._queue_emailer)
        self.consume_channel.basic_consume(queue=self._queue_emailer,
                                           on_message_callback=self.callback, auto_ack=True)
        self.publish_channel = self.connection.channel()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.publish_channel.close()
        self.consume_channel.close()

    def init_consume(self):
        self.consume_channel.start_consuming()

    def publish(self, method: str, body: dict):
        """
            **publish**
                will publish messages back to the routing target
                publishes messages to one of the routing targets selected.
        :return:
        """
        properties = pika.BasicProperties(method)
        bytes_body: bytes = bytes(json.dumps(body), encoding='utf-8')
        self.publish_channel.basic_publish(exchange='', routing_key=self._routing_target, body=bytes_body,
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
        **get_email_fields**
            with email data fetch email fields

        :param data:
        :return: tuple
        """
        email: str = data.get('email')
        subject: str = data.get('subject')
        text: str = data.get('text')
        html: str = data.get('html')
        o_tag: str = data.get('o_tag')
        job_name: str = data.get('job_name')
        time_scheduled: datetime = data.get('time_scheduled')
        return email, subject, text, html, o_tag, job_name, time_scheduled

    def callback(self, ch, method, properties, body: bytes):
        """
        **callback**
            called to process incoming messages sent to emailer

        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        from main import emailer_instance
        data: dict = json.loads(body.decode("UTF-8"))
        if properties.content_type == "send-email":
            # call send email here
            email, subject, text, html, o_tag = self.get_email_fields(data=data)
            emailer_instance._send_with_mailgun_rest_api(to_list=[email], subject=subject, text=text,
                                                         html=html, o_tag=o_tag)
            return 'OK', 200

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
            _job_name: str = emailer_instance._create_job_name(header_name=job_name)

            response = asyncio.run(
                emailer_instance._base_email_scheduler(func=emailer_instance._send_with_mailgun_rest_api,
                                                       kwargs=_kwargs, job_name=_job_name,
                                                       time_scheduled=time_scheduled))
            self.publish(method='email-scheduled', body=response)

            return 'OK', 200
