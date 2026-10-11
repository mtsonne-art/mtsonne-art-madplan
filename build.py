#!/usr/bin/env python3
"""Byg madplan-siden og ugens mail ud fra weeks.json.

Brug: python3 build.py <side-url> [maildir]
Skriver index.html i repoets rod (Netlify serverer den) samt
<maildir>/mail.html og <maildir>/mail.txt for den nyeste uge.
weeks.json holdes på de 5 nyeste uger (nyeste først).
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CATS = ["Kød og fisk", "Frugt og grønt", "Mejeri (laktosefri)", "Kolonial"]


def num(n):
    n = round(n, 1)
    return (str(int(n)) if n == int(n) else str(n)).replace(".", ",")


def aggregate(week):
    items, order, pantry = {}, [], []
    for d in week["dishes"]:
        for g in d["ingredients"]:
            k = (g["item"], g["unit"])
            if k not in items:
                items[k] = dict(g, amount=0)
                order.append(k)
            items[k]["amount"] += g["amount"]
        for p in d.get("pantry", []):
            if p not in pantry:
                pantry.append(p)
    return [items[k] for k in order], pantry


def mail(week, url):
    e = html.escape
    items, pantry = aggregate(week)
    h = ['<div style="font-family:Arial,sans-serif;max-width:640px;color:#1d2a22;line-height:1.5">']
    h.append(f'<p style="font-size:17px"><b>Der er en ny madplan for uge {week["week"]}.</b><br>'
             f'Vælg retter og byg indkøbslisten her: <a href="{e(url)}">{e(url)}</a></p>')
    h.append(f'<p style="color:#5d6b61">5 forslag, alt fra {e(week["store"])}. Indkøbslisten herunder dækker alle 5 retter; '
             'på siden kan I fravælge retter, så listen kun dækker dem I vælger.</p>')
    h.append('<h2 style="margin-bottom:4px">Ugens retter</h2>')
    for i, d in enumerate(week["dishes"], 1):
        h.append(f'<p style="margin:10px 0"><b>{i}. {e(d["name"])}</b> ({e(d["time"])})<br>{e(d["desc"])}</p>')
    h.append(f'<h2 style="margin:24px 0 4px">Indkøbsliste ({e(week["store"])}, alle 5 retter)</h2>')
    for c in CATS:
        rows = [i for i in items if i["cat"] == c]
        if not rows:
            continue
        h.append(f'<h4 style="margin:12px 0 2px">{e(c)}</h4><ul style="margin-top:0">')
        for i in rows:
            offer = f' – <b>tilbud {e(i["offer"])}</b>' if i.get("offer") else ""
            h.append(f'<li>{num(i["amount"])} {e(i["unit"])} {e(i["item"])}{offer}</li>')
        h.append("</ul>")
    if pantry:
        h.append(f'<p style="color:#5d6b61"><b>Tjek om I har hjemme:</b> {e(", ".join(pantry).lower())}.</p>')
    h.append('<h2 style="margin:28px 0 4px">Opskrifter</h2>')
    for d in week["dishes"]:
        h.append(f'<h3 style="margin:18px 0 4px">{e(d["name"])}</h3><p style="margin:0;color:#5d6b61">{e(d["time"])} · 4 personer</p><ul>')
        for g in d["ingredients"]:
            h.append(f'<li>{num(g["amount"])} {e(g["unit"])} {e(g["item"])}</li>')
        for p in d.get("pantry", []):
            h.append(f"<li>{e(p)}</li>")
        h.append("</ul><ol>")
        for s in d["steps"]:
            h.append(f"<li>{e(s)}</li>")
        h.append("</ol>")
    if week.get("note"):
        h.append(f'<p style="color:#5d6b61;font-size:13px;margin-top:24px">{e(week["note"])}</p>')
    h.append("</div>")

    t = [f"Der er en ny madplan for uge {week['week']}.", f"Vælg retter og byg indkøbslisten her: {url}", "",
         "Ugens retter:"]
    t += [f"{i}. {d['name']} ({d['time']})" for i, d in enumerate(week["dishes"], 1)]
    t += ["", f"Indkøbsliste ({week['store']}, alle 5 retter):"]
    for c in CATS:
        rows = [i for i in items if i["cat"] == c]
        if rows:
            t.append(c + ": " + ", ".join(f"{num(i['amount'])} {i['unit']} {i['item']}" + (f" (tilbud {i['offer']})" if i.get("offer") else "") for i in rows))
    if pantry:
        t.append("Tjek om I har hjemme: " + ", ".join(pantry).lower() + ".")
    t += ["", "Opskrifter:"]
    for d in week["dishes"]:
        t += ["", f"{d['name']} ({d['time']})"]
        t += [f"- {num(g['amount'])} {g['unit']} {g['item']}" for g in d["ingredients"]] + [f"- {p}" for p in d.get("pantry", [])]
        t += [f"{i}. {s}" for i, s in enumerate(d["steps"], 1)]
    return "\n".join(h), "\n".join(t)


def main():
    url = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    path = os.path.join(HERE, "weeks.json")
    weeks = json.load(open(path, encoding="utf-8"))
    weeks.sort(key=lambda w: (w["year"], w["week"]), reverse=True)
    weeks = weeks[:5]
    json.dump(weeks, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    data = json.dumps(weeks, ensure_ascii=False).replace("</", "<\\/")
    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    os.makedirs(out, exist_ok=True)
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(tpl.replace("/*__DATA__*/", data))
    mh, mt = mail(weeks[0], url)
    open(os.path.join(out, "mail.html"), "w", encoding="utf-8").write(mh)
    open(os.path.join(out, "mail.txt"), "w", encoding="utf-8").write(mt)
    print(f"Uger: {[w['week'] for w in weeks]}; skrev index.html og mail.html/mail.txt i {out}")


if __name__ == "__main__":
    main()
