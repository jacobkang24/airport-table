import sqlite3
from p2app.events.countries import (CountrySearchResultEvent, Country, CountryLoadedEvent, CountrySavedEvent, SaveCountryFailedEvent)
from p2app.events.app import ErrorEvent

class Country_Engine:
    def __init__(self, connection):
        self.connection = connection

    def country_search(self, event):
        if self.connection:
            try:
                if event.country_code() and event.name():
                    cursor = self.connection.execute("SELECT * FROM country WHERE country_code=? and name=?", (str(event.country_code()), str(event.name())))
                elif event.country_code():
                    cursor = self.connection.execute("SELECT * FROM country WHERE country_code=?", str(event.country_code()))
                elif event.name():
                    cursor = self.connection.execute("SELECT * FROM country WHERE name=?", str(event.name()))
                else:
                    return
                for row in cursor.fetchall():
                    country = Country(*row)
                    yield CountrySearchResultEvent(country)
            except sqlite3.Error as error:
                yield ErrorEvent(str(error))


    def load_country(self, event):
        if self.connection:
            try:
                cursor = self.connection.execute("SELECT * FROM country WHERE country_id=?", (event.country_id()))
                row = cursor.fetchone()
                if row:
                    country = Country(*row)
                    yield CountryLoadedEvent(country)
            except sqlite3.Error as error:
                yield ErrorEvent(str(error))


    def save_new_country(self, event):
        if not self.connection:
            yield SaveCountryFailedEvent("No database connection")
            return

        country = event.country()
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO country (country_code, name) VALUES (?, ?)", (country.country_code, country.name))
            self.connection.commit()
            country_id = cursor.lastrowid

            saved_country = Country(country_id, country.country_code, country.name)
            yield CountrySavedEvent(saved_country)
        except sqlite3.Error as error:
            yield ErrorEvent(str(error))


    def save_country(self, event):
        if not self.connection:
            yield SaveCountryFailedEvent("No database connection")
            return

        country = event.country()
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE country SET country_code=?, name=? WHERE country_id=?", (country.country_code, country.name, country.country_id))
            self.connection.commit()

            yield CountrySavedEvent(country)
        except sqlite3.Error as error:
            yield SaveCountryFailedEvent(str(error))

