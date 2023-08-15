from selenium.common.exceptions import WebDriverException


class InvalidParsingDataException(WebDriverException):
    def __init__(self, message):
        super().__init__(message)
