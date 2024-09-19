import sqlite3
from p2app.events.continents import (ContinentSearchResultEvent, Continent, ContinentLoadedEvent, ContinentSavedEvent, SaveContinentFailedEvent)
from p2app.events.app import ErrorEvent

class Continent_Engine:
    def __init__(self, connection):
        self.connection = connection


    def continent_search(self, event):
        if self.connection:
            try:
                if event.continent_code() and event.name():
                    cursor = self.connection.execute("SELECT * FROM continent WHERE continent_code=? and name=?", (str(event.continent_code()), str(event.name())))
                elif event.continent_code():
                    cursor = self.connection.execute("SELECT * FROM continent WHERE continent_code=?", str(event.continent_code()))
                elif event.name():
                    cursor = self.connection.execute("SELECT * FROM continent WHERE name=?", str(event.name()))
                else:
                    return
                for row in cursor.fetchall():
                    continent = Continent(*row)
                    yield ContinentSearchResultEvent(continent)
            except sqlite3.Error as error:
                yield ErrorEvent(str(error))


    def load_continent(self, event):
        if self.connection:
            try:
                cursor = self.connection.execute("SELECT * FROM continent WHERE continent_id=?", (event.continent_code()))
                row = cursor.fetchone()
                if row:
                    continent = Continent(*row)
                    yield ContinentLoadedEvent(continent)
            except sqlite3.Error as error:
                yield ErrorEvent(str(error))

    def save_new_continent(self, event):
        if not self.connection:
            yield SaveContinentFailedEvent("No database connection")
            return

        continent = event.continent()
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO continent (continent_code, name) VALUES (?, ?)",(continent.continent_code, continent.name))
            self.connection.commit()
            continent_id = cursor.lastrowid

            saved_continent = Continent(continent_id, continent.continent_code, continent.name)
            yield ContinentSavedEvent(saved_continent)
        except sqlite3.Error as error:
            yield ErrorEvent(str(error))

    def save_continent(self, event):
        if not self.connection:
            yield SaveContinentFailedEvent("No database connection")
            return

        continent = event.continent()
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE continent SET continent_code=?, name=? WHERE continent_id=?",
                           (continent.continent_code, continent.name, continent.continent_id))
            self.connection.commit()

            yield ContinentSavedEvent(continent)
        except sqlite3.Error as error:
            yield SaveContinentFailedEvent(str(error))
