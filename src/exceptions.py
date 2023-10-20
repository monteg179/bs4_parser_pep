class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class DeliveryError(Exception):
    pass


class RequestError(DeliveryError):

    MESSAGE = 'Ошибка получения {url}'

    def __init__(self, url: str) -> None:
        self.__url = url

    def __str__(self) -> str:
        return type(self).MESSAGE.format(url=self.__url)


class ResponseError(DeliveryError):

    MESSAGE = 'Ошибка получения {url}, status={status}'

    def __init__(self, url: str, status: int) -> None:
        self.__url = url
        self.__status = status

    def __str__(self) -> str:
        return type(self).MESSAGE.format(url=self.__url, status=self.__status)
