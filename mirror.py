import datetime
import pathlib

import jinja2

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('template'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

outdir = pathlib.Path("output")

title = "Welcome to mirror.ifca.es"
template_date = "FIXME FIXME"
date = datetime.datetime.now()

for t in ("index.html", "about.html"):
    with open(outdir / t, "w") as f:
        tpl = env.get_template(t)
        f.write(tpl.render(
            title=title,
            template_date=template_date,
            date=date)
        )
