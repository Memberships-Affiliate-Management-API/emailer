
class EventProcessor:
    """
    **Class EventProcessor**
        depends on pika to provide a queue of events to subscribe to
    """

    def __init__(self):
        self.event_queue: list = []

    def subscribe_to_event(self, callback_func, event_name):
        pass

    def create_event(self, event_name, channel):
        pass

    def un_subscribe(self, callback_func, event_name):
        pass
