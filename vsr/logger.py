import os
import logging
from logging.handlers import TimedRotatingFileHandler


class Logger:
    def __init__(self,
                 debug: bool = False,
                 logger_name: str | None = None,
                 log_to_file: bool = False,
                 logs_filename: str | None = None,
                 logs_path: str | None = None,
                 backup_log_files_count: int = 7):

        self.debug_mode = debug

        self.log_to_file = log_to_file
        self.backup_log_files_count = backup_log_files_count
        self.logs_path = self.__set_logs_path(logs_filename, logs_path)

        self.__logger = logging.getLogger(__name__ if logger_name is None else logger_name)

        self.__setup()

    def get_logger(self):
        return self.__logger

    @staticmethod
    def from_context(logger_name: str):
        return logging.getLogger(logger_name)

    def __set_logs_path(self, filename: str | None, path: str | None) -> str | None:
        if filename is None or path is None:
            return None

        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        return os.path.join(path, filename)

    def __setup(self):
        self.__logger.setLevel("DEBUG" if self.debug_mode else "INFO")
        self.__setup_serial()

        if self.logs_path is not None and self.log_to_file:
            self.__setup_file()

    def __setup_serial(self):
        formatter = self.__get_formatter(with_day=False)

        console_logger = logging.StreamHandler()
        console_logger.setFormatter(formatter)

        self.__logger.addHandler(console_logger)

    def __setup_file(self):
        formatter = self.__get_formatter()

        file_handler = TimedRotatingFileHandler(filename=self.logs_path,
                                                when="midnight",
                                                encoding="utf-8",
                                                backupCount=self.backup_log_files_count)
        file_handler.setFormatter(formatter)

        self.__logger.addHandler(file_handler)

    def __get_formatter(self, with_day: bool = True) -> logging.Formatter:
        format = "%Y-%m-%d %H:%M:%S" if with_day else "%H:%M:%S"

        formatter = logging.Formatter(
            "{asctime} - {name} - {levelname} - {message}",
            style="{",
            datefmt=format,
        )

        return formatter
