import os
import consul
import json
import re


CONSUL_PATH = 'consul.consul-1.cecolo.gofg.net'
CONSUL_PORT = 8500
CONSUL_ENCODING = 'UTF-8'
SEARCH_RECURSE = True
#SEARCH_INDEX = 'salt-private/prod/mx-1.cecolo.gofg.net/customers/COMS'
SEARCH_INDEX = ''
INPUT_FILE = 'input/input.conf'
OUTPUT_FILE = 'output/output.txt'
KEYS_FILE = 'output/keys.txt'


RE_CONFIG_IGNORE = re.compile('\s*#.*')



def print_values(values, indent):
    val = json.loads(str(values))
    for i,v in val.items():
        print(i, v)

def proccess_config():
    searches = []
    with open(INPUT_FILE) as input:
        lines = input.readlines()
    for line in lines:
        line = line.strip()
        while len(line) > 0 and line[-1] == os.linesep:
            line = line[0:-1]
        if len(line) == 0:
            print('CONFIG: Ignoring empty line.')
        elif RE_CONFIG_IGNORE.match(line):
            print(f'CONFIG: Ignoring config line {line}.')
        else:
            searches.append(re.compile(line, re.IGNORECASE))

    return searches

def search_item(item, searches):
    res = []
    value = item['Value'].decode(CONSUL_ENCODING) if (('Value' in item) and item['Value'] is not None) else None
    for s in searches:
        if s.match(item['Key']):
            res.append(('KEY', s.pattern))
        if (value is not None) and s.search(value, re.MULTILINE):
            res.append(('VALUE', s.pattern))

    return (res, item['Key'], value)

def writeline_output(line, output):
    output.write(line+os.linesep)

def write_item_output(matches, output):
    items, key, value = matches
    writeline_output('', output)
    writeline_output('='*50, output)
    writeline_output(key, output)
    writeline_output('='*50, output)
    for where, pattern in items:
        writeline_output(f'Pattern: {pattern}', output)
        writeline_output(f'In: {where}', output)
        writeline_output('=' * 50, output)
    writeline_output('=' * 50, output)
    if value is not None:
        writeline_output(value, output)
    else:
        writeline_output('NONE value', output)

def write_item_keys(matches, output_keys):
    items, key, _ = matches
    output_keys.write(key + os.linesep)
    for where, pattern in items:
        output_keys.write(f'   {pattern}, {where}{os.linesep}')

def search_items(index, consul_instance, searches, output, output_keys):
    index, data = consul_instance.kv.get(index, recurse=SEARCH_RECURSE)
    for item in data:
        res = search_item(item, searches)
        if len(res[0]) > 0:
            write_item_output(res, output)
            write_item_keys(res, output_keys)


def main():
    searches = proccess_config()
    consul_instance = consul.Consul(host=CONSUL_PATH, port=CONSUL_PORT)
    with open(OUTPUT_FILE, 'w') as output, open(KEYS_FILE, 'w') as output_keys:
        search_items(SEARCH_INDEX, consul_instance, searches, output, output_keys)

if __name__ == '__main__':
    main()