import argparse
import pathlib
import itertools
import sys

import docker
import tqdm
from compose import config


version = "0.4.0"


def save(args, client, service, print):
    image = service["image"]
    real_images = client.images.list(image)
    if not real_images:
        print(f"{image}: missed (pull or build image)")
        sys.exit(1)
    if len(real_images) > 1:
        names = ", ".join(set(itertools.chain.from_iterable(i.tags for i in real_images)))
        print(f"{image}: specify image name more precisely (candidates: {names})")
        sys.exit(1)
    path = args.output / f"{service['name']}.tar"
    if path.exists() and not args.overwrite:
        print(f"{image} skip ({path} already exists)")
        return
    print(f"{image} saving...")
    args.output.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        for chunk in real_images[0].save():
            f.write(chunk)


def load(args, client, service, print):
    print(f"{service['image']} loading...")
    with (args.input / f"{service['name']}.tar").open("rb") as f:
        i, *_ = client.images.load(f)
        i.tag(service['image'])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=False, action="store_true", help="show version")
    parser.add_argument("--timeout", default=60, type=int, help="docker connection timeout [default: %(default)s]")
    parser.add_argument("-f", "--file", default="docker-compose.yml", type=pathlib.Path,
                        help="specify an alternate compose file [default: %(default)s]")
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
    env = config.environment.Environment.from_env_file(path.parent)
    details = config.find(path.parent, [path.name], env)
    resolved = config.load(details)
    for s in resolved.services:
        if "image" not in s:
            raise RuntimeError(f"Service {s['name']!r} have no 'image' field")
        yield s


def main():
    args = parse_args()
    if args.version:
        print(version)
        return
    services = list(gen_services(args.file.resolve()))
    client = docker.from_env(timeout=args.timeout)
    viewed = set()
    with tqdm.tqdm(total=len(services)) as pbar:
        for service in services:
            if service["image"] not in viewed:
                args.function(args, client, service, print=pbar.write)
            viewed.add(service["image"])
            pbar.update(1)
