# Docker compose transfer
Missed `save`/`load` commands for docker compose.

## Installation
``` bash
python -m pip install docker-compose-transfer
```

## Requirements
* python 3.6+
* docker

## License
`docker-compose-transfer` is offered under the WTFPL license.

## Usage

``` bash
$ docker-compose-transfer --help
usage: docker-compose-transfer [-h] [-v] [-f FILE] {save,load} ...

positional arguments:
  {save,load}

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Show version
  -f FILE, --file FILE  Specify an alternate compose file [default: docker-
                        compose.yml]
```
