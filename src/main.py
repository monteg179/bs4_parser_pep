import logging
import re

from requests import Session
from requests_cache import CachedSession
from tqdm import tqdm
from urllib.parse import urljoin

from configs import (
    configure_argument_parser,
    configure_logging,
)
from constants import (
    BASE_DIR,
    MAIN_DOC_URL,
    MAIN_PEP_URL,
)
from exceptions import (
    DeliveryError,
    ParserFindTagException,
)
from outputs import control_output
from peps import Peps
from utils import (
    download_file,
    make_soup,
)


def whats_new(session: Session) -> list[tuple[str, str, str]]:
    whats_new_url = MAIN_DOC_URL + 'whatsnew/'
    soup = make_soup(session, whats_new_url)
    ul_tag = soup.html.body.select_one('#what-s-new-in-python ul')
    if ul_tag is None:
        message = 'Не найден <ul>'
        logging.error(message)
        raise ParserFindTagException(message)
    a_tags = ul_tag.select('li.toctree-l1 > a')
    links = [
        a_tag['href']
        for a_tag in a_tags
    ]
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for link in tqdm(links):
        url = urljoin(whats_new_url, link)
        soup = make_soup(session, url)
        header_tag = soup.html.body.find(name='h1')
        if header_tag is None:
            result.append((url, '', ''))
            continue
        header = str(next(header_tag.strings))
        authors_tag = header_tag.find_next_sibling('dl')
        if authors_tag is None:
            result.append((url, header, ''))
            continue
        authors = authors_tag.text.strip().replace('\n', ' ')
        result.append((url, header, authors))
    return result


def latest_versions(session: Session) -> list[tuple[str, str, str]]:
    soup = make_soup(session, MAIN_DOC_URL)
    ul_tags = soup.html.body.select('div.sphinxsidebarwrapper ul')
    for ul_tag in ul_tags:
        if 'All versions' in ul_tag.text:
            a_tags = ul_tag.find_all(name='a')
            break
    else:
        raise ParserFindTagException()
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    a_tags = ul_tag.find_all(name='a')
    result = []
    for a_tag in tqdm(a_tags):
        text_match = re.search(pattern, a_tag.text)
        if text_match is None:
            version, status = a_tag.text, ''
        else:
            version, status = text_match.groups()
        result.append((a_tag['href'], version, status))
    return result


def download(session: CachedSession) -> None:
    download_url = MAIN_DOC_URL + 'download.html'
    soup = make_soup(session, download_url)
    table_tag = soup.html.body.select_one('table.docutils')
    if table_tag is None:
        raise ParserFindTagException()
    pattern = r'.+pdf-a4\.zip$'
    a_tag = table_tag.find(name='a', attrs={'href': re.compile(pattern)})
    if table_tag is None:
        raise ParserFindTagException()
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    url = urljoin(download_url, a_tag['href'])
    file_name = url.split('/')[-1]
    path = downloads_dir / file_name
    download_file(url, path)
    logging.info(f'Архив был загружен и сохранён: {path}')


def pep(session: Session) -> list[tuple[str, str]]:
    instance = Peps(MAIN_PEP_URL)
    instance(session)
    result = [('Статус', 'Количество')]
    result.extend(
        [(key, str(value)) for key, value in instance.statistics.items()]
    )
    total = sum(instance.statistics.values())
    result.append(('Total', str(total)))
    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    logging.info('Парсер запущен!')
    try:
        session = CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        result = MODE_TO_FUNCTION[parser_mode](session)
        if result is not None:
            control_output(result, args)
    except (DeliveryError, ParserFindTagException):
        logging.info('Парсер завершил работу c ошибкой')
    except Exception as error:
        logging.error(f'error: {type(error)} = {error}')
        logging.info('Парсер завершил работу c ошибкой')
    else:
        logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
