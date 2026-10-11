# Familiens madplan

Ugentlig madplan for familien, hostet på Netlify. Hver lørdag lægges en ny uge ind.

- `weeks.json` – arkivet (de 5 nyeste uger, nyeste først)
- `template.html` – siden
- `build.py` – `python3 build.py <side-url> <maildir>` bygger `index.html` og ugens mail
- `index.html` – den færdige side (genereres, ret ikke i den direkte)
