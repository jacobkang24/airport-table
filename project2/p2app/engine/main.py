# p2app/engine/main.py
#
# ICS 33 Spring 2024
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.
from .connect_countries import Country_Engine
from .connect_continents import Continent_Engine
from .connect_regions import Region_Engine
import _sqlite3
from p2app.events.database import *
from p2app.events.app import QuitInitiatedEvent, EndApplicationEvent, ErrorEvent
from p2app.events.countries import StartCountrySearchEvent, LoadCountryEvent, SaveNewCountryEvent, SaveCountryEvent
from p2app.events.continents import StartContinentSearchEvent, LoadContinentEvent, SaveNewContinentEvent, SaveContinentEvent
from p2app.events.regions import StartRegionSearchEvent, LoadRegionEvent, SaveNewRegionEvent, SaveRegionEvent

class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self.connection = None
        self.country_engine = None
        self.continent_engine = None
        self.region_engine = None


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        event_type = type(event)
        if self.connection is None:
            if event_type != OpenDatabaseEvent:
                yield ErrorEvent("Database not opened yet")
                return
            else:
                yield from self._open_database(event)
                return

        if event_type == OpenDatabaseEvent:
            yield ErrorEvent("Database already opened")
            return
        elif event_type == CloseDatabaseEvent:
            yield from self._close_database()
            return
        elif event_type == QuitInitiatedEvent:
            yield EndApplicationEvent()
            return

        if self.country_engine is None:
            self.country_engine = Country_Engine(self.connection)
        if self.continent_engine is None:
            self.continent_engine = Continent_Engine(self.connection)
        if self.region_engine is None:
            self.region_engine = Region_Engine(self.connection)

        if event_type == StartCountrySearchEvent:
            yield from self.country_engine.country_search(event)
        elif event_type == LoadCountryEvent:
            yield from self.country_engine.load_country(event)
        elif event_type == SaveNewCountryEvent:
            yield from self.country_engine.save_new_country(event)
        elif event_type == SaveCountryEvent:
            yield from self.country_engine.save_country(event)

        elif event_type == StartContinentSearchEvent:
            yield from self.continent_engine.continent_search(event)
        elif event_type == LoadContinentEvent:
            yield from self.continent_engine.load_continent(event)
        elif event_type == SaveNewContinentEvent:
            yield from self.continent_engine.save_new_continent(event)
        elif event_type == SaveContinentEvent:
            yield from self.continent_engine.save_continent(event)

        elif event_type == StartRegionSearchEvent:
            yield from self.region_engine.region_search(event)
        elif event_type == LoadRegionEvent:
            yield from self.region_engine.load_region(event)
        elif event_type == SaveNewRegionEvent:
            yield from self.region_engine.save_new_region(event)
        elif event_type == SaveRegionEvent:
            yield from self.region_engine.save_region(event)

    def _open_database(self, event):
        try:
            self.connection = _sqlite3.Connection(event.path())
            self.connection.execute("PRAGMA foreign_keys = ON;")
            yield DatabaseOpenedEvent(event.path())
        except _sqlite3.Error as error:
            yield DatabaseOpenFailedEvent(str(error))

    def _close_database(self):
        if self.connection is not None:
            try:
                self.connection.close()
                self.connection = None
                yield DatabaseClosedEvent()
            except _sqlite3.Error as error:
                yield ErrorEvent(str(error))


