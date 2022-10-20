Searches Consul database for input regular matches.

## config
  * CONSUL_PATH, DNS/IP of consul instance 
  * CONSUL_PORT, port of Consul HTTP
  * CONSUL_ENCODING, encoding of Consul values
  * SEARCH_RECURSE, search recursively
  * INPUT_FILE, input file with regular expressions
  * OUTPUT_FILE, output file - detailed
  * KEYS_FILE, output file - only key and short info (matched pattern, whether matched key or value)

## notes
  * search is case-insensitive
  * search in value is multiline

## config file
  * two search definitions, simple and regex:
    * simple: is escaped and completed by .* from both sides (text on line)
    * regex: is used as is (text on line prefixed with '\s*re:\s*')
```
.*bakaláři.*

#test.*
.*CRAD-0009.*
re:alza.*
```
  * each line is one pattern
  * empty lines are ignored
  * lines starting # are ignored