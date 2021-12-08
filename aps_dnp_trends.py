#!/usr/bin/env python3

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

def scrape(abstract):
    date = abstract.find(name = 'meta', attrs = {'name': 'citation_date'})['content']
    [identifier] = [heading.text.split(':')[1].strip() for heading in abstract.find_all(name = 'h3') if 'Abstract' in heading.text]
    [session] = [heading.text for heading in abstract.find_all(name = 'h3') if 'Session' in heading.text]
    title = abstract.find(name = 'meta', attrs = {'name': 'citation_title'})['content']
    authors = abstract.find(name = 'meta', attrs = {'name': 'citation_authors'})['content']
    try:
        [text] = [division.text for division in abstract.find_all('div', {'class': 'largernormal', 'style': 'margin-bottom: 1em;'})]
    except ValueError:
        text = ''
    return date, identifier, session, title, authors, text

def main():

    epitome_url = 'https://meetings.aps.org/Meeting/DNP16/APS_epitome'
    epitome_response = requests.get(url = epitome_url)
    epitome_soup = BeautifulSoup(markup = epitome_response.content, features = 'html.parser')

    session_links = sorted(set([link for link in epitome_soup.find_all(name = 'a', href = True)
                                if 'Session' in link['href']]), key = lambda tag: tag['href'])
    for session_link in session_links:
        session_url = urljoin(epitome_url, session_link['href'])
        session_response = requests.get(url = session_url)
        session_soup = BeautifulSoup(markup = session_response.content, features = 'html.parser')

        abstract_links = [link for link in session_soup.find_all(name = 'a', href = True)
                          if '/Session/' in link['href'] and 'showAbstract' not in link['href']]
        for abstract_link in abstract_links:
            abstract_url = urljoin(session_url, abstract_link['href'])
            abstract_response = requests.get(url = abstract_url)
            abstract_soup = BeautifulSoup(markup = abstract_response.content, features = 'html.parser')
            info = scrape(abstract_soup)
            assert info[1] == abstract_link.text.split(':')[0].strip()

if __name__ == '__main__':
    main()
