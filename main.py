import os

from config import *
import consul
import json
import re

INPUT_FILE = 'input/input.conf'
OUTPUT_FILE = 'output/output.txt'
KEYS_FILE = 'output/keys.txt'


c = consul.Consul('consul.consul-1.cecolo.gofg.net')

def print_values(values, indent):
    val = json.loads(str(values))
    for i,v in val.items():
        print(i, v)

def proccess_config():
    searches = []
    with open(INPUT_FILE) as input:
        lines = input.readlines()
    for line in lines:
        while line[-1] == os.linesep:
            line = line[0:-1]
        searches.append(re.compile(line, re.IGNORECASE))

    return searches

def search_item(item, searches):
    for s in searches:
        value = item['Value'].decode('UTF-8') if (('Value' in item) and item['Value'] is not None) else None
        if s.match(item['Key']):
            return True, 'Key', s.pattern
        if (value is not None) and s.match(value, re.MULTILINE):
            return True, 'Value', s.pattern

    return False, None, None

def writeline_output(line, output):
    output.write(line+os.linesep)

def write_item_output(where, pattern, item, output):
    writeline_output('', output)
    writeline_output('='*50, output)
    writeline_output(item['Key'], output)
    writeline_output('='*50, output)
    writeline_output(f'Pattern: {pattern}', output)
    writeline_output(f'In: {where}', output)
    writeline_output('=' * 50, output)
    writeline_output(item["Value"].decode('UTF-8'), output)


def search_items(index, searches, output, output_keys):
    index, data = c.kv.get(index, recurse=True)
    for item in data:
        res, where, pattern = search_item(item, searches)
        if res:
            write_item_output(where, pattern, item, output)
            output_keys.write(item['Key'] + os.linesep)
            output_keys.write(f'   {pattern}, {where}{os.linesep}')


def main():
    searches = proccess_config()
    with open(OUTPUT_FILE, 'w') as output, open(KEYS_FILE, 'w') as output_keys:
        search_items('', searches, output, output_keys)


main()