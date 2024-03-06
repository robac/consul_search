import datetime
import consul
import re
import pandas as pd
from collections import defaultdict
import logging

RE_CONFIG_REGEX = re.compile('\s*re:\s*(.*)')

class SearchOptions:
    def __init__(self, search_keys, search_values, regular, index):
        self.SEARCH_KEYS = search_keys
        self.SEARCH_VALUES = search_values
        self.INDEX = index
        self.REGULAR = regular

    def __reduce__(self):
        return (self.SEARCH_KEYS, self.SEARCH_VALUES, self.REGULAR, self.INDEX)

    def __str__(self):
        return f"{self.SEARCH_KEYS}  {self.SEARCH_VALUES}  {self.REGULAR}  {self.INDEX}"



class ConsulSearch:
    def __init__(self):
        self.last_update = None
        self.in_progress = False
        self.timer_run = 0
        self.consul_index = None
        self.consul_data = None
        self.config = None
        self.sections = None

    @property
    def can_process(self):
        return self.last_update and not self.in_progress

    def load_sections(self):
        sections = defaultdict()
        sections[""] = None
        for item in self.consul_data:
            key = item["Key"]
            path = key.split("/")
            if len(path) > 1:
                section = '/'.join(path [0:-1])
                sections[section] = None
        self.sections = sections

    def load_data(self, config):
        logging.info(f"load started, host {self.config['host']}")
        self.config = config
        consul_instance = consul.Consul(host=self.config["host"], port=self.config["port"])
        try:
            self.consul_index, self.consul_data = consul_instance.kv.get("", recurse=True)
            self.last_update = datetime.datetime.now()
            self.load_sections()
        except Exception as e:
            self.consul_index, self.consul_data, self.last_update = (None, None, None)
            logging.error(f"loading host {self.config['host']}, %s", e)
        logging.info(f"load finished, host {self.config['host']}")


    def _prepare_searches(self, searches, options : SearchOptions):
        result = []
        for search in searches:
            if options.REGULAR:
                pattern = search
            else:
                pattern = f'{re.escape(search)}'
            result.append(re.compile(pattern, re.IGNORECASE | re.MULTILINE))
            print(f'CONFIG: installed pattern {pattern}')
        return result

    def _search_item(self, item, searches, excludes, options : SearchOptions):
        """
        Search in one item for match with 'searches'.
        :param item: item to process
        :param searches: list of searched patterns
        :return: ((search_found_in_key, search_found_in_value), key, value)
        """
        encoding = self.config["encoding"]
        if excludes is not None and re.match(excludes, item['Key']):
            return ((False, False), None)
            print("excluded {item['Key']}")

        value = item['Value'].decode(encoding) if (('Value' in item) and item['Value'] is not None) else None

        found_key = False
        found_value = False
        for s in searches:
            if options.SEARCH_KEYS and s.search(item['Key']):
                found_key = True
            if options.SEARCH_VALUES and (value is not None) and s.search(value):
                found_value = True

        return ((found_key, found_value), item['Key'], value)

    def _search_items(self, searches, excludes, options : SearchOptions):
        print(f"Search start. Data version: {self.last_update}")
        df_structure = {
            'inkey': [],
            'invalue': [],
            'key': [],
            'value' : []
        }

        results = pd.DataFrame(df_structure)
        count = 0
        for item in self.consul_data:
            res = self._search_item(item, searches, excludes, options)
            if (res[0][0] or res[0][1]):
                new_row = {'inkey': res[0][0], 'invalue': res[0][1], 'key': res[1], 'value' : res[2]}
                results.loc[len(results)] = new_row
        return results

    def _prepare_excludes(self):
        if "exclude" not in self.config:
            return None

        lst = []
        for item in self.config["exclude"]:
            pattern1 = f"^{re.escape(item)}$"
            pattern2 = f"^{re.escape(item)}/.+$"
            lst.append(pattern1)
            lst.append(pattern2)

        return "|".join(lst)

    def search(self, searches, options : SearchOptions):
        if self.consul_data is None:
            return None

        searches = self._prepare_searches(searches, options)
        excludes = self._prepare_excludes()
        print (f"Excludes {excludes}")
        return self._search_items(searches, excludes, options)
