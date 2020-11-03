#!/usr/bin/python3

import datetime
import os.path
import pathlib
import sys

path = pathlib.Path(__file__).parent / ".."  # noqa
path = path.resolve().as_posix()  # noqa
sys.path.append(path)  # noqa

import filelock
import jinja2
import yaml

import mirror

MIRROR_DATA = mirror.MIRROR_DATA
MIRROR_LOCK = mirror.MIRROR_LOCK
ROOT = pathlib.Path(__file__).parent / ".."

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(ROOT / 'template'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

outdir = ROOT / "output"

title = "Welcome to mirror.ifca.es"
date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

lock = filelock.FileLock(MIRROR_LOCK, timeout=10)

with lock:
    if not MIRROR_DATA.exists():
        data = {}
    else:
        with open(MIRROR_DATA, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

for t in ("index.html", "about.html", "stats.html"):
    with open(outdir / t, "w") as f:
        tpl = env.get_template(t)
        template_date = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(tpl.filename)
        ).strftime("%Y-%m-%d %H:%M:%S")
        f.write(
            tpl.render(
                title=title,
                template_date=template_date,
                date=date,
                mirror_data=data
            )
        )

tpl = env.get_template("stats_individual.html")
for mirror_name, mirror_data in data.items():
    with open(outdir / f"stats_{mirror_name}.html", "w") as f:
        f.write(
            tpl.render(
                title=title,
                template_date=template_date,
                date=date,
                mirror_data=mirror_data,
                mirror=mirror_name,
            )
        )
