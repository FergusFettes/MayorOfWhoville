from concurrent.futures import ThreadPoolExecutor
from threading import local
import time
import random as ra
import logging
import asyncio


FORMAT = "%(levelname)s@%(name)s(%(asctime)s) -- \"%(message)s\""
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

class TheLandOfWhos:
    TOWNSHIPS = set([
    "Whoville",
    "Pooville",
    "Trueville",
    "Flooville",
    "Shoeville",
    "Blueville",
    "Screwville",
    "Whatatodoville",
    "Grueville",
    "Jewville",
    "Stewville",
    "Brewville",
    "Gooville",
    ])

    LOCATION_OF_THE_MAYOR_OF_WHOVILLE = "Whoville"
    TRAVELLING_STRING = "Undefined!"
    MAYOR_WHEREABOUTS_KNOWN = False

    PLACES_CHECKED = set()

    def choose_other_town(self):
        other_towns = list(self.TOWNSHIPS)
        other_towns.remove(self.LOCATION_OF_THE_MAYOR_OF_WHOVILLE)
        return other_towns[ra.randint(0, len(self.TOWNSHIPS) - 2)]

    def choose_unexamined_town(self):
        unexamined_towns = list(self.TOWNSHIPS.difference(self.PLACES_CHECKED))
        return unexamined_towns[ra.randint(0, len(unexamined_towns) - 1)]

    async def hunter_loop(self):
        while True:
            if self.MAYOR_WHEREABOUTS_KNOWN:
                await asyncio.sleep(0.1)
            else:
                self.check_random_town()

    async def check_random_town(self):
            town = self.choose_unexamined_town()
            logging.info("Checking {}".format(town))
            await asyncio.sleep((ra.random() + 0.1) * 3)
            if self.LOCATION_OF_THE_MAYOR_OF_WHOVILLE == town:
                logging.info("Found the mayor in {}!".format(town))
                self.MAYOR_WHEREABOUTS_KNOWN = True
                self.PLACES_CHECKED = set()
            elif self.LOCATION_OF_THE_MAYOR_OF_WHOVILLE == self.TRAVELLING_STRING:
                logging.info("Spies report the mayor was seen in a roadside tavern near {}!".format(town))
                self.PLACES_CHECKED.add(town)


    async def escapade_loop(self):
        while True:
            if self.MAYOR_WHEREABOUTS_KNOWN:
                self.escape_to_some_other_town()
            else:
                await asyncio.sleep(0.1)

    async def escape_to_some_other_town(self):
            logging.info("The mayor escaped! Keep on the hunt!")
            destination = self.choose_other_town()
            self.LOCATION_OF_THE_MAYOR_OF_WHOVILLE = self.TRAVELLING_STRING
            self.MAYOR_WHEREABOUTS_KNOWN = False
            logging.info("Mayor is travelling to {}".format(destination))
            await asyncio.sleep(ra.randint(1, 10))
            self.LOCATION_OF_THE_MAYOR_OF_WHOVILLE = destination

    async def hunters(self):
        tasks =[]
        tasks.append(self.escapade_loop())
        tasks.append(self.hunter_loop())
        await asyncio.gather(*tasks)

if __name__=="__main__":
    l = TheLandOfWhos()
    loop = asyncio.get_event_loop().run_until_complete(l.hunters())
