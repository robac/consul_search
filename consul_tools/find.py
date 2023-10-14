import asyncio
import os
import consul
import json
import re

RE_CONFIG_REGEX = re.compile('\s*re:\s*(.*)')

def search_item(item, searches, encoding):
    res = []
    value = item['Value'].decode(encoding) if (('Value' in item) and item['Value'] is not None) else None
    for s in searches:
        if s.match(item['Key']):
            res.append(('KEY', s.pattern))
        if (value is not None) and s.search(value, re.MULTILINE):
            res.append(('VALUE', s.pattern))

    return (res, item['Key'], value)

async def search_items(index, consul_instance, searches, recurse=False, encoding="UTF-8"):
    results = []
    index, data = asyncio.to_thread(consul_instance.kv.get(index, recurse=recurse))
    count = 0
    for item in data:
        res = search_item(item, searches, encoding)
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


async def find(what, config):
    searches = prepare_searches(what)
    consul_instance = consul.Consul(host=config["CONSUL_PATH"], port=config["CONSUL_PORT"])
    return await search_items(config["SEARCH_INDEX"], consul_instance, searches, config["SEARCH_RECURSE"], config["CONSUL_ENCODING"])