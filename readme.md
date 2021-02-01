# Docker compose transfer
Missed `save`/`load` commands for docker compose.

## Installation
``` bash
python -m pip install docker-compose-transfer
```

## Requirements
* python 3.5+
* docker

## License
`docker-compose-transfer` is offered under the WTFPL license.

## Usage

``` bash
$ docker-compose-transfer --help
usage: docker-compose-transfer [-h] [--version] [--timeout TIMEOUT]
                               [--use-service-image-name-as-filename]
                               [-f FILE]
                               {save,load} ...

positional arguments:
  {save,load}

optional arguments:
  -h, --help            show this help message and exit
  --version             show version
  --timeout TIMEOUT     docker connection timeout [default: 60]
  --use-service-image-name-as-filename
                        Support legacy naming behavior
  -f FILE, --file FILE  specify an alternate compose file
```
