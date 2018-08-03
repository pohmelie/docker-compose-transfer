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
usage: docker-compose-transfer [-h] [--version] [--timeout TIMEOUT] [-f FILE]
                               {save,load} ...

positional arguments:
  {save,load}

optional arguments:
  -h, --help            show this help message and exit
  --version             show version
  --timeout TIMEOUT     docker connection timeout [default: 60.0]
  -f FILE, --file FILE  specify an alternate compose file [default: docker-
                        compose.yml]
```
