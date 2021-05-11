import argparse
import pathlib
import itertools
import sys
import urllib

import docker
import tqdm
from compose import config


version = "0.8.0"


def _resolve_name(args, service):
    if args.use_service_image_name_as_filename:
        return urllib.parse.quote(service["image"], safe="")
    return service["name"]


def save(args, client, service, print):
    image = service["image"]
    real_images = [i for i in client.images.list() if image in i.tags]
    if not real_images:
        print("{}: missed (pull, build or specify precisely image name)".format(image))
        sys.exit(1)
    if len(real_images) > 1:
        names = ", ".join(set(itertools.chain.from_iterable(i.tags for i in real_images)))
        print("{}: specify image name more precisely (candidates: {})".format(image, names))
        sys.exit(1)
    path = args.output / "{}.tar".format(_resolve_name(args, service))
    if path.exists() and not args.overwrite:
        print("{} skip ({} already exists)".format(image, path))
        return
    print("{} saving...".format(image))
    args.output.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        for chunk in real_images[0].save():
            f.write(chunk)


def load(args, client, service, print):
    print("{} loading...".format(service["image"]))
    path = args.input / "{}.tar".format(_resolve_name(args, service))
    with path.open("rb") as f:
        i, *_ = client.images.load(f)
        i.tag(service["image"])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=False, action="store_true", help="show version")
    parser.add_argument("--timeout", default=60, type=int, help="docker connection timeout [default: %(default)s]")
    parser.add_argument("--use-service-image-name-as-filename", default=False, action="store_true",
                        help="Support legacy naming behavior")
    parser.add_argument("-f", "--file", default=None, type=pathlib.Path,
                        help="specify an alternate compose file")
    sub_commands = parser.add_subparsers(dest="command")
    sub_commands.required = True
    p = sub_commands.add_parser("save")
    p.set_defaults(function=save)
    p.add_argument("-o", "--output", type=pathlib.Path, default=".",
                   help="output directory [default: %(default)s]")
    p.add_argument("--overwrite", action="store_true", default=False,
                   help="overwrite if exist [default: %(default)s]")
    p = sub_commands.add_parser("load")
    p.set_defaults(function=load)
    p.add_argument("-i", "--input", type=pathlib.Path, default=".",
                   help="input directory [default: %(default)s]")
    return parser.parse_args()


def gen_services(path):
    parent = str(path.parent)
    env = config.environment.Environment.from_env_file(parent)
    details = config.find(parent, [path.name], env)
    resolved = config.load(details)
    for s in resolved.services:
        if "image" not in s:
            raise RuntimeError("Service {!r} have no 'image' field".format(s["name"]))
        yield s


def main():
    args = parse_args()
    if args.version:
        print(version)
        return
    if args.file is None:
        files = ["docker-compose.yml", "docker-compose.yaml"]
    else:
        files = [args.file]
    for file in files:
        path = pathlib.Path(file)
        if not path.exists():
            continue
        path = path.resolve()
        services = list(gen_services(path))
        break
    else:
        raise RuntimeError("Files does not exists {!r}".format(files))
    client = docker.from_env(timeout=args.timeout)
    viewed = set()
    with tqdm.tqdm(total=len(services)) as pbar:
        services.sort(key=lambda s: s["name"])
        for service in services:
            if service["image"] not in viewed:
                args.function(args, client, service, print=pbar.write)
            viewed.add(service["image"])
            pbar.update(1)
