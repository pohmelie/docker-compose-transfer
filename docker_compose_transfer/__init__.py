import argparse
import pathlib
import itertools
import urllib
import sys

import docker
import yaml
import tqdm


version = "0.1.0"


def save(args, client, image, print):
    real_images = client.images.list(image)
    if not real_images:
        print(f"{image}: missed (pull or build image)")
        sys.exit(1)
    if len(real_images) > 1:
        names = ", ".join(set(itertools.chain.from_iterable(i.tags for i in real_images)))
        print(f"{image}: specify image name more precisely (candidates: {names})")
        sys.exit(1)
    escaped = urllib.parse.quote(image, safe="")
    path = args.output / f"{escaped}.tar"
    if path.exists() and not args.overwrite:
        print(f"{image} skip ({path} already exists)")
        return
    print(f"{image} saving...")
    args.output.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        for chunk in real_images[0].save():
            f.write(chunk)


def load(args, client, image, print):
    print(f"{image} loading...")
    escaped = urllib.parse.quote(image, safe="")
    with (args.input / f"{escaped}.tar").open("rb") as f:
        i, *_ = client.images.load(f)
        i.tag(image)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=False, action="store_true", help="show version")
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


def gen_images_list(path):
    compose = yaml.load(path.read_text())
    for name, config in compose["services"].items():
        if "image" not in config:
            raise RuntimeError(f"Service {name!r} have no 'image' field")
        yield config["image"]


def main():
    args = parse_args()
    if args.version:
        print(version)
        return
    client = docker.from_env()
    config_images = list(gen_images_list(args.file))
    with tqdm.tqdm(total=len(config_images)) as pbar:
        for image in config_images:
            args.function(args, client, image, print=pbar.write)
            pbar.update(1)
