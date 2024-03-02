import datetime
import random

import consul
import re
import pandas as pd

RE_CONFIG_REGEX = re.compile('\s*re:\s*(.*)')


class ConsulSearch:
    def __init__(self):
        self.last_update = None
        self.in_progress = False
        self.timer_run = 0
        self.consul_index = None
        self.consul_data = None
        self.config = None

    @property
    def can_process(self):
        return self.last_update and not self.in_progress

    def load_data(self, config):
        print("Load started")
        self.config = config
        consul_instance = consul.Consul(host=self.config["CONSUL_PATH"], port=self.config["CONSUL_PORT"])
        try:
            self.consul_index, self.consul_data = consul_instance.kv.get(self.config["SEARCH_INDEX"], recurse=self.config["SEARCH_RECURSE"])
            self.last_update = datetime.datetime.now()
        except Exception as e:
            self.consul_index, self.consul_data, self.last_update = (None, None, None)
            print(e)
        print("load finished")
        print(f"index: {self.consul_index}")
        print(len(self.consul_data) if self.consul_data else 0)


    def _prepare_searches(self, searches):
        result = []
        for search in searches:
            m = RE_CONFIG_REGEX.match(search)
            if m:
                pattern = m.group(1)
            else:
                pattern = f'.*{re.escape(search)}.*'
            result.append(re.compile(pattern, re.IGNORECASE))
            print(f'CONFIG: installed pattern {pattern}')
        return result

    def _search_item(self, item, searches):
        """
        Search in one item for match with 'searches'.
        :param item: item to process
        :param searches: list of searched patterns
        :return: ((search_found_in_key, search_found_in_value), key, value)
        """
        encoding = self.config["CONSUL_ENCODING"]
        value = item['Value'].decode(encoding) if (('Value' in item) and item['Value'] is not None) else None
        found_key = False
        found_value = False
        for s in searches:
            if s.match(item['Key']):
                found_key = True
            if (value is not None) and s.search(value, re.MULTILINE):
                found_value = True

        return ((found_key, found_value), item['Key'], value)

    def _search_items(self, searches):
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

            res = self._search_item(item, searches)
            if (res[0][0] or res[0][1]):
                new_row = {'inkey': res[0][0], 'invalue': res[0][1], 'key': res[1], 'value' : res[2]}
                results.loc[len(results)] = new_row
        return results

    def search(self, searches):
        if self.consul_data is None:
            return None

        searches = self._prepare_searches(searches)
        return self._search_items(searches)
