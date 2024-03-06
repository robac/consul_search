import datetime
import pprint

import consul
import re
import pandas as pd
from collections import defaultdict

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
        self.excludes = None

    @property
    def can_process(self):
        return self.last_update and not self.in_progress

    def load_sections(self):
        sections = {}
        for item in self.consul_data:
            items = item.split('/')
            if len(items) > 1:
                helper = sections
                for j in items[0:-1]:
                    if j not in helper:
                        helper[j] = {}
                    helper = helper[j]
                helper = None

        self.sections = sections

    def load_data(self, config):
        print("Load started")
        self.config = config
        self.excludes = self._prepare_excludes()

        consul_instance = consul.Consul(host=self.config["host"], port=self.config["port"])
        data = defaultdict()
        try:
            self.consul_index, consul_data = consul_instance.kv.get("", recurse=True)
            self.last_update = datetime.datetime.now()

            for item in consul_data:
                if self.excludes is not None and re.match(self.excludes, item['Key']):
                    print("excluded {item['Key']}")
                else:
                    data[item["Key"]] = item["Value"].decode(config["encoding"]) if ("Value" in item and item['Value'] is not None) else None
            self.consul_data = data
            self.load_sections()
        except Exception as e:
            self.consul_index, self.consul_data, self.last_update = (None, None, None)
            print(e)
        print("load finished")
        print(f"index: {self.consul_index}")
        print(len(self.consul_data) if self.consul_data else 0)


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

    def _search_item(self, item, searches, options : SearchOptions):
        """
        Search in one item for match with 'searches'.
        :param item: item to process
        :param searches: list of searched patterns
        :return: ((search_found_in_key, search_found_in_value), key, value)
        """
        key, value = item

        found_key = False
        found_value = False
        for s in searches:
            if options.SEARCH_KEYS and s.search(key):
                found_key = True
            if options.SEARCH_VALUES and (value is not None) and s.search(value):
                found_value = True

        return ((found_key, found_value), key, value)

    def _search_items(self, searches, options : SearchOptions):
        print(f"Search start. Data version: {self.last_update}")
        df_structure = {
            'inkey': [],
            'invalue': [],
            'key': [],
            'value' : []
        }

        results = pd.DataFrame(df_structure)
        count = 0
        for key, value in self.consul_data.items():
            res = self._search_item((key, value), searches, options)
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

        return re.compile("|".join(lst))

    def search(self, searches, options : SearchOptions):
        if self.consul_data is None:
            return None

        searches = self._prepare_searches(searches, options)
        return self._search_items(searches, options)
