import logging
from pathlib import (
    Path,
)
from http import (
    HTTPStatus,
)

from bs4 import (
    BeautifulSoup,
)
from requests import (
    RequestException,
    Response,
    Session,
)
from tqdm import (
    tqdm,
)
import urllib3

from exceptions import (
    ParserFindTagException,
    RequestError,
    ResponseError,
)


def download_file(url: str, path: Path) -> None:
    kibibyte = 1024
    http = urllib3.PoolManager()
    try:
        response = http.request('GET', url, preload_content=False)
        status = response.status
        if not status == HTTPStatus.OK:
            logging.error(ResponseError.MESSAGE.format(url, status))
            raise ResponseError(url, status)
        file_size = int(response.headers.get('content-length', 0))
        block_size = kibibyte * 100
        with open(path, 'wb') as file:
            with tqdm(total=file_size, unit_scale=True) as bar:
                for chunk in response.stream(block_size):
                    file.write(chunk)
                    bar.update(len(chunk))
    except urllib3.exceptions.RequestError:
        logging.error(RequestError.MESSAGE.format(url))
        raise RequestError(url)
    finally:
        response.release_conn()


def get_response(session: Session, url: str) -> Response:
    try:
        response = session.get(url)
    except RequestException:
        logging.error(RequestError.MESSAGE.format(url))
        raise RequestError(url)
    else:
        status = response.status_code
        if not status == HTTPStatus.OK:
            logging.error(ResponseError.MESSAGE.format(url, status))
            raise ResponseError(url, status)
        return response


def make_soup(session: Session, url: str, encoding: str = 'utf-8',
              features: str = 'lxml') -> BeautifulSoup:
    response = get_response(session, url)
    response.encoding = encoding
    return BeautifulSoup(response.text, features=features)


def find_tag(tag, name: str, attrs=None):
    result = tag.find(name, attrs=(attrs or {}))
    if result is None:
        error_msg = f'Не найден тег {name} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return result
