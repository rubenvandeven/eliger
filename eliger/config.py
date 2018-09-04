import json
import os

class Config(object):
    """docstring for Config."""
    config = {}

    def __init__(self, filename, settings):
        super(Config, self).__init__()
        self.filename = filename

        if not os.path.exists(self.filename):
            print("! Status does not exist, creating {} on save".format(self.filename))
            self.config = settings
        else:
            with open(self.filename, 'r') as fp:
                self.config = json.load(fp)

    def save(self):
        with open(self.filename, 'w') as fp:
            json.dump(self.config, fp)


    def set(self, key, value):
        self.config[key] = value
        self.save()

    def get(self, key, default_value = None):
        return self.config.get(key, default_value)
