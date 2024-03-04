Searches Consul database for input regular matches.

## config


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