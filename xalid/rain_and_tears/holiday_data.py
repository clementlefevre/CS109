#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
Little python script for converting tables from "www.schulferien.org" to csv tables with a specific format.

@author: Yorick Zeschke
@date: 21.10.2016
@requirements: python3, bs4, geocoder
"""

from urllib import urlopen
import csv

from bs4 import BeautifulSoup
import geocoder


class HolidayData:
    def __init__(self, info=None, autorun=False):
        """
        :param info: (list) for custom tables (has to be in format: [(year, country, url_to_get_table), ...]
        :param autorun: (boolean) if activated, the class will get all tables from the info list and write them to
         csv files (necessary for updating tables or if you just downloaded the script and don'T have any tables)
        """

        if info is None:
            self.HOLIDAY_INFO = [
                (2013, 'germany', "http://www.schulferien.org/deutschland/ferien/2013/"),
                (2014, 'germany', "http://www.schulferien.org/deutschland/ferien/2014/"),
                (2015, 'germany', "http://www.schulferien.org/deutschland/ferien/2015/"),
                (2016, 'germany', "http://www.schulferien.org/deutschland/ferien/2016/"),
                (2017, 'switzerland', "http://www.schulferien.org/deutschland/ferien/2017/"),
                (2013, 'switzerland', "http://www.schulferien.org/schweiz/ferien/2013/"),
                (2014, 'switzerland', "http://www.schulferien.org/schweiz/ferien/2014/"),
                (2015, 'switzerland', "http://www.schulferien.org/schweiz/ferien/2015/"),
                (2016, 'switzerland', "http://www.schulferien.org/schweiz/ferien/2016/"),
                (2017, 'switzerland', "http://www.schulferien.org/schweiz/ferien/2017/"),
            ]

        else: self.HOLIDAY_INFO = info

        if autorun is True:
            for y, c, u in self.HOLIDAY_INFO:
                self.table_to_csv(u, c, y)
                print('Table written!')

    def table_to_csv(self, url, country, year):
        """
        Gets the table from 'www.schulferien.org' and writes it into a csv file
        :param url: (str) where to get the table (accepts only from 'www.schulferien.org')
        :param country: (str) ["germany"|"switzerland"] for naming csv files
        :param year: (int) also for naming
        """

        table = self.__get_table(url, country)
        self.__write_csv(table, year, country)

    def location_holidays(self, lon, lat, year):
        """
        Finds out the holidays (for the given year) of the state at the given location
        in longitude (float) and latitude (float). !Tables have to exist, for using this function!
        :return: (list) [['<date from>', '<date to>'], ...]
        """

        state, country = self.__get_state(lon, lat)
        return self.__get_holidays(state, country.lower(), year)

    def __get_table(self, url, country):
        soup = BeautifulSoup(urlopen(url).read())
        table = []

        for tr in soup.find('tbody').find_all('tr'):
            state = tr.find('span', {'class': 'sf_table_index_row_value'}).text.strip()
            if country == 'switzerland':
                if 'Alle Schulen' not in state: continue  # equivocal data (only some schools have holidays)
                state = ' '.join(state.split()[:-2])  # different parsing (remove 'Alle Schulen'

            for td in tr.find_all('span', {'class': 'nowrap'}):
                date_pair = td.text.strip().split()
                if date_pair == '-': continue  # no HOLIDAY_INFO
                elif '/' in date_pair: continue  # equivocal data (two possible dates)
                elif len(date_pair) == 1:  # only one day holiday (probably additional to the weekend)
                    table.append([state, date_pair[0], date_pair[0]])
                    continue

                table.append([state, date_pair[0], date_pair[2]])

        return table

    def __write_csv(self, table, year, country):
        with open('holidays_{y}_{c}.csv'.format(y=str(year), c=country), "wb") as fhdlr:
            writer = csv.writer(fhdlr, delimiter=' ', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['Bundesland', 'Von', 'Bis'])
            for row in table:
                writer.writerow([el.encode('utf-8') for el in row])

    def __get_holidays(self, state, country, year):
        with open('holidays_{y}_{c}.csv'.format(y=year, c=country), "r") as fhdlr:
            reader = csv.reader(fhdlr, delimiter=' ', quotechar='"', quoting=csv.QUOTE_ALL)
            return [[el.decode('utf-8') for el in row] for row in reader if state in row]  # only dates

    def __get_state(self, lon, lat):
        location = geocoder.google([lon, lat], method='reverse')
        return location.state_long, location.country_long


if __name__ == '__main__':
    holiday = HolidayData(autorun=True)
    print(holiday.location_holidays(52.524451, 13.345186, 2016))  # DILAX coordinates
