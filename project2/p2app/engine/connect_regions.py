import sqlite3
from p2app.events.regions import (RegionSearchResultEvent, Region, RegionLoadedEvent, RegionSavedEvent, SaveRegionFailedEvent)
from p2app.events.app import ErrorEvent

class Region_Engine:
    def __init__(self, connection):
        self.connection = connection

    def region_search(self, event):
        if self.connection:
            try:
                if event.region_code() and event.name():
                    cursor = self.connection.execute("SELECT * FROM region WHERE region_code=? and name=?", (str(event.region_code()), str(event.name())))
                elif event.region_code():
                    cursor = self.connection.execute("SELECT * FROM region WHERE region_code=?", str(event.region_code()))
                elif event.name():
                    cursor = self.connection.execute("SELECT * FROM region WHERE name=?", str(event.name()))
                else:
                    return
                for row in cursor.fetchall():
                    region = Region(*row)
                    yield RegionSearchResultEvent(region)
            except sqlite3.Error as error:
                yield ErrorEvent(str(error))


    def load_region(self, event):
        if self.connection:
            try:
                cursor = self.connection.execute("SELECT * FROM region WHERE region_id=?", (event.region_id()))
                row = cursor.fetchone()
                if row:
                    region = Region(*row)
                    yield RegionLoadedEvent(region)
            except sqlite3.Error as error:
                yield ErrorEvent(str(error))

    def save_new_region(self, event):
        if not self.connection:
            yield SaveRegionFailedEvent("No database connection")
            return

        region = event.region()
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO region (region_code, name) VALUES (?, ?)",
                           (region.region_code, region.name))
            self.connection.commit()
            region_id = cursor.lastrowid

            saved_region = Region(region_id, region.region_code, region.name)
            yield RegionSavedEvent(saved_region)
        except sqlite3.Error as error:
            yield ErrorEvent(str(error))


    def save_region(self, event):
        if not self.connection:
            yield SaveRegionFailedEvent("No database connection")
            return

        region = event.region()
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE region SET region_code=?, name=? WHERE region_id=?",
                           (region.region_code, region.name, region.region_id))
            self.connection.commit()

            yield RegionSavedEvent(region)
        except sqlite3.Error as error:
            yield SaveRegionFailedEvent(str(error))