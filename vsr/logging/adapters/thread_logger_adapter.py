import logging


class ThreadLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f'[{self.extra["thread_uid"]}] - {msg}', kwargs
