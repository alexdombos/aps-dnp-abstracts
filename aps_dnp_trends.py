#!/usr/bin/env python3

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

def scrape(abstract):
    date = abstract.find(name = 'meta', attrs = {'name': 'citation_date'})['content']
    [session] = [heading.text for heading in abstract.find_all(name = 'h3') if 'Session' in heading.text]
    title = abstract.find(name = 'meta', attrs = {'name': 'citation_title'})['content']
    authors = abstract.find(name = 'meta', attrs = {'name': 'citation_authors'})['content']
    return date, session, title, authors

def main():

    epitome_url = 'https://meetings.aps.org/Meeting/DNP19/APS_epitome'
    epitome_response = requests.get(url = epitome_url)
    epitome_soup = BeautifulSoup(markup = epitome_response.content, features = 'html.parser')

    session_links = [link for link in epitome_soup.find_all(name = 'a', href = True)
                     if 'Session' in link['href']]
    for session_link in session_links:
        session_url = urljoin(epitome_url, session_link['href'])
        session_response = requests.get(url = session_url)
        session_soup = BeautifulSoup(markup = session_response.content, features = 'html.parser')

        abstract_links = [link for link in session_soup.find_all(name = 'a', href = True)
                          if 'Session' in link['href'] and 'showAbstract' not in link['href']]
        for abstract_link in abstract_links:
            abstract_url = urljoin(session_url, abstract_link['href'])
            abstract_response = requests.get(url = abstract_url)
            abstract_soup = BeautifulSoup(markup = abstract_response.content, features = 'html.parser')

if __name__ == '__main__':
    main()
