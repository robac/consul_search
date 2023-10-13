import os
import consul
import json
import re


CONSUL_PATH = 'consul.consul-1.cecolo.gofg.net'
CONSUL_PORT = 8500
CONSUL_ENCODING = 'UTF-8'
SEARCH_RECURSE = True
SEARCH_INDEX = ''
INPUT_FILE = 'input/input.conf'
OUTPUT_FILE = 'output/output.txt'
KEYS_FILE = 'output/keys.txt'

RE_CONFIG_REGEX = re.compile('\s*re:\s*(.*)')

def search_item(item, searches):
    res = []
    value = item['Value'].decode(CONSUL_ENCODING) if (('Value' in item) and item['Value'] is not None) else None
    for s in searches:
        if s.match(item['Key']):
            res.append(('KEY', s.pattern))
        if (value is not None) and s.search(value, re.MULTILINE):
            res.append(('VALUE', s.pattern))

    return (res, item['Key'], value)

def search_items(index, consul_instance, searches):
    results = []
    index, data = consul_instance.kv.get(index, recurse=SEARCH_RECURSE)
    count = 0
    for item in data:
        res = search_item(item, searches)
        if len(res[0]) > 0:
            results.append(res)
    return results

def prepare_searches(searches):
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


async def find(what):
    searches = prepare_searches(what)
    consul_instance = consul.Consul(host=CONSUL_PATH, port=CONSUL_PORT)
    return search_items(SEARCH_INDEX, consul_instance, searches)