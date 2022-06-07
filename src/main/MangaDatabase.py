import pickle

class MangaDatabase:

    def __init__(self, data=None):
        if data is None:
            self.data = []
        else:
            self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    def load(self, filename):
        """Loads data from a file."""
        self.data = pickle.load(open(filename, "rb"))
        print(f'LOADED {filename}')

    def save(self, filename):
        """Stores data in a file."""
        pickle.dump(self.data, open(filename, "wb"))
        print(f'SAVED {filename}')

    def merge(self, database2):
        """Merges with a second database

        Input:
            database2 = Of Database class. Overwrites data in the database that calls merge.
        """
        titles = {manhwa.title: index for index, manhwa in enumerate(self.data)}

        for manhwa in database2.data:
            if manhwa.title in titles.keys():
                # overwrite existing title
                self.data[titles[manhwa.title]] = manhwa
            else:
                # add to database
                self.data.append(manhwa)

    def add(self, manhwa):
        """Adds a new manhwa to the database.

        Input:
            manhwa = The manhwa to be added. Must be a descendent of the Manhwa class.
        """
        self.merge(MangaDatabase([manhwa]))

    def update(self):
        """Calls the update method on every manhwa in the database."""
        for manhwa in self.data:
            try:
                manhwa.update()
            except:
                print(f'{manhwa.title} - FAILED TO UPDATE')

        return self

    def update_classes(self):
        """Calls the update_class function on every manhwa in the database."""
        new_data = [update_class(data) for data in self.data]

        if len(new_data) == len(self.data):
            self.data = new_data
            print('CLASSES SUCCESSFULLY UPDATED')
        else:
            print('ERROR UPDATING')

    def show(self, show_expanded=False):
        """Displays information pertaining to each manhwa.

        Input:
            show_expanded = Boolean value. If true, displays additional data.
        """
        for index, manhwa in enumerate(self.data):
            print(f'[{index}] ', end='')

            if show_expanded:
                manhwa.show()
                print('')
            else:
                print(f'{manhwa.title}')

    def sort(self):
        """Sorts the database alphabetically by class"""
        self.data = sorted(self.data, key=(lambda data: data.__class__.__name__))
        print('SORTED ALPHABETICALLY BY CLASS')

    def unread(self, chapters=1):
        """""Returns a database containing unread manhwa

        Input:
            chapters = The minimum amount of unread chapters.
        """
        return MangaDatabase([manhwa for manhwa in self.data if manhwa.unread() >= chapters])

    def rated(self, rating=0, greater=False):
        """Returns a database containing all the manhwa of a specified rating

        Input:
            rating  = The rating to compare against
            greater = Boolean value. If True, returns everything greater than or equal to the rating. Otherwise
                      returns everything equal to the rating.
        """
        if greater:
            return MangaDatabase([manhwa for manhwa in self.data if int(manhwa.rating) >= rating])
        else:
            return MangaDatabase([manhwa for manhwa in self.data if int(manhwa.rating) == rating])

    def get_checked_before(self, date_to_check):
        """Returns a database containing all the manhwa that was checked before a certain date.

        Input:
            date_to_check = A date in %d/%m/%y format.
        """

        date_to_check = datetime.datetime.strptime(date_to_check, '%d/%m/%y')
        return MangaDatabase([manhwa for manhwa in self.data if manhwa.last_checked < date_to_check])

    def get_asura(self):
        """Returns a database containing all the manhwa published by AsuraScans"""
        return MangaDatabase([manhwa for manhwa in self.data if isinstance(manhwa, AsuraScans)])

    def get_reaper(self):
        """Returns a database containing all the manhwa published by ReaperScans"""
        return MangaDatabase([manhwa for manhwa in self.data if isinstance(manhwa, ReaperScans)])

    def get_line(self):
        """Returns a database containing all the manhwa published by LineWebtoon"""
        return MangaDatabase([manhwa for manhwa in self.data if isinstance(manhwa, LineWebtoon)])

    def get_plus(self):
        """Returns a database containing all the manhwa published by MangaPlus"""
        return MangaDatabase([manhwa for manhwa in self.data if isinstance(manhwa, MangaPlus)])