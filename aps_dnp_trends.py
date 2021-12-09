#!/usr/bin/env python3

from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime
from urllib.parse import urljoin
import requests

Abstract = namedtuple('Abstract', ['date', 'identifier', 'session', 'title', 'authors', 'text'])

def all_aps_dnp_years():
    return {2005: 'HAW05',
            2006: 'DNP06',
            2007: 'DNP07',
            2008: 'DNP08',
            2009: 'HAW09',
            2010: 'DNP10',
            2011: 'DNP11',
            2012: 'DNP12',
            2013: 'DNP13',
            2014: 'HAW14',
            2015: 'DNP15',
            2016: 'DNP16',
            2017: 'DNP17',
            2018: 'HAW18',
            2019: 'DNP19',
            2020: 'DNP20',
            2021: 'DNP21'}

def scrape_session(session):
    try:
        dates = [date.text.split(',', 1)[1].strip() for date in session.find_all('a', href = False) if date.text and date.text != 'Not Participating']
        assert all(date == dates[0] for date in dates)
        date_text = dates[0]
    except IndexError:
        date_text = session.find_all('font', attrs = {'size': -1})[0].text.split('\n')[1].split(',', 1)[1].strip()

    date = datetime.strptime(date_text, "%B %d, %Y").strftime("%m/%d/%Y")
    [session] = [heading.text for heading in session.find_all('h3') if all(part in heading.text for part in ('Session', ':'))]
    return Abstract(date = date, identifier = None, session = session,
                    title = None, authors = None, text = None)

def scrape_abstract(abstract):
    date = abstract.find(name = 'meta', attrs = {'name': 'citation_date'})['content']
    [identifier] = [heading.text.split(':')[1].strip() for heading in abstract.find_all(name = 'h3') if 'Abstract' in heading.text]
    [session] = [heading.text for heading in abstract.find_all(name = 'h3') if 'Session' in heading.text]
    title = abstract.find(name = 'meta', attrs = {'name': 'citation_title'})['content']
    authors = abstract.find(name = 'meta', attrs = {'name': 'citation_authors'})['content']
    try:
        [text] = [division.text for division in abstract.find_all('div', {'class': 'largernormal', 'style': 'margin-bottom: 1em;'})]
    except ValueError:
        text = ''
    return Abstract(date = date, identifier = identifier, session = session,
                    title = title, authors = authors, text = text)

def main():

    aps_dnp_years = all_aps_dnp_years()
    for year, year_url_segment in aps_dnp_years.items():
        epitome_url = f'https://meetings.aps.org/Meeting/{year_url_segment}/APS_epitome'
        epitome_response = requests.get(url = epitome_url)
        epitome_soup = BeautifulSoup(markup = epitome_response.content, features = 'html.parser')

        session_links = sorted(set([link for link in epitome_soup.find_all(name = 'a', href = True)
                                if 'Session' in link['href']]), key = lambda tag: tag['href'])
        for session_link in session_links:
            session_url = urljoin(epitome_url, session_link['href'])
            session_response = requests.get(url = session_url)
            session_soup = BeautifulSoup(markup = session_response.content, features = 'html.parser')

            session_data = scrape_session(session_soup)

            abstract_links = [link for link in session_soup.find_all(name = 'a', href = True)
                              if '/Session/' in link['href'] and 'showAbstract' not in link['href']]
            for abstract_link in abstract_links:
                abstract_url = urljoin(session_url, abstract_link['href'])
                abstract_response = requests.get(url = abstract_url)
                abstract_soup = BeautifulSoup(markup = abstract_response.content, features = 'html.parser')

                identifier = abstract_link.text.split(':')[0].strip()
                abstract_data = scrape_abstract(abstract_soup)
                assert abstract_data.date == session_data.date
                assert abstract_data.identifier == identifier
                assert abstract_data.session == session_data.session

if __name__ == '__main__':
    main()
