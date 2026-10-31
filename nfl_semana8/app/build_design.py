# Genera app/index.html a partir del diseño de Claude Design (design_src.html): incrusta props.js y props_data.json.
import json, pathlib
here = pathlib.Path(__file__).resolve().parent; root = here.parent
src = (here / 'design_src.html').read_text(encoding='utf-8')
js = (root / 'props.js').read_text(encoding='utf-8')
data = json.dumps(json.load(open(root / 'props_data.json', encoding='utf-8')), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
assert src.count('/*PROPS_JS*/') == 1 and src.count('/*DATA_JSON*/') == 1
out = src.replace('/*PROPS_JS*/', js, 1).replace('/*DATA_JSON*/', data, 1)
(here / 'index.html').write_text(out, encoding='utf-8'); print('index.html', len(out.encode('utf-8')), 'bytes')
