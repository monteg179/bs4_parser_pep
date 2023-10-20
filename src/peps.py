import logging

from requests import (
    Session,
)
from tqdm import (
    tqdm,
)
from urllib.parse import (
    urljoin,
)


from exceptions import (
    ParserFindTagException,
)
from utils import (
    make_soup,
)


class PepCard:

    __slots__ = ('__status_key', '__url', '__status')

    def __init__(self, status_key: str, url: str) -> None:
        self.__status_key = status_key
        self.__url = url
        self.__status = None

    def scraping(self, session: Session) -> None:
        soup = make_soup(session, self.__url)
        dl_tag = soup.html.body.select_one('#pep-content > dl')
        if dl_tag is None:
            logging.warning('Не найден тэг dl')
            raise ParserFindTagException()
        status_string = dl_tag.find(string='Status')
        if status_string is None:

            raise ParserFindTagException()
        dd_tag = status_string.parent.next_sibling.next_sibling
        self.__status = str(dd_tag.string)

    @property
    def url(self) -> str:
        return self.__url

    @property
    def status_key(self) -> str:
        return self.__status_key

    @property
    def status(self) -> str:
        return self.__status


class Peps:

    ACTIVE_STATUS = 'Active'
    ACCEPTED_STATUS = 'Accepted'
    DEFERRED_STATUS = 'Deferred'
    DRAFT_STATUS = 'Draft'
    FINAL_STATUS = 'Final'
    PROVISIONAL_STATUS = 'Provisional'
    REJECTED_STATUS = 'Rejected'
    SUPERSEDED_STATUS = 'Superseded'
    WITHDRAWN_STATUS = 'Withdrawn'

    STATUSES = (
        ACTIVE_STATUS,
        ACCEPTED_STATUS,
        DEFERRED_STATUS,
        DRAFT_STATUS,
        FINAL_STATUS,
        PROVISIONAL_STATUS,
        REJECTED_STATUS,
        SUPERSEDED_STATUS,
        WITHDRAWN_STATUS
    )

    EXPECTED_STATUS = {
        'A': (ACTIVE_STATUS, ACCEPTED_STATUS),
        'D': (DEFERRED_STATUS,),
        'F': (FINAL_STATUS,),
        'P': (PROVISIONAL_STATUS,),
        'R': (REJECTED_STATUS,),
        'S': (SUPERSEDED_STATUS,),
        'W': (WITHDRAWN_STATUS,),
        '': (DRAFT_STATUS, ACTIVE_STATUS),
    }

    def __init__(self, url: str) -> None:
        self.__url = url
        self.__cards = []
        self.__statistics = {}
        for status in type(self).STATUSES:
            self.__statistics[status] = 0

    def __call__(self, session: Session) -> None:
        self.scraping(session)
        self.processing()

    def scraping(self, session: Session) -> None:
        self.__cards = []
        soup = make_soup(session, self.__url)
        tbody_tag = soup.html.body.select_one('#numerical-index tbody')
        if tbody_tag is None:
            raise ParserFindTagException()
        tr_tags = tbody_tag.find_all(name='tr')
        for tr_tag in tqdm(tr_tags):
            td_tags = tr_tag.find_all(name='td')
            if len(td_tags) < 2:
                continue
            a_tag = td_tags[1].find(name='a')
            if a_tag is None:
                continue
            card = PepCard(
                status_key=td_tags[0].string[1:],
                url=urljoin(self.__url, a_tag['href'])
            )
            card.scraping(session)
            self.__cards.append(card)

    def processing(self) -> None:
        for key in self.__statistics.keys():
            self.__statistics[key] = 0
        for card in self.__cards:
            if card.status not in type(self).STATUSES:
                logging.warning(f'Непонятный status: {card.status}')
                continue
            if card.status not in type(self).EXPECTED_STATUS[card.status_key]:
                logging.warning('status не соответствует status_key')
            self.__statistics[card.status] += 1

    @property
    def cards(self) -> list[PepCard]:
        return self.__cards

    @property
    def statistics(self) -> dict[str, int]:
        return self.__statistics
