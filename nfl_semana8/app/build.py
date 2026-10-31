# Genera app/index.html: incrusta props.js y props_data.json en app/src.html
import json, pathlib
here = pathlib.Path(__file__).resolve().parent
root = here.parent
src = (here / 'src.html').read_text(encoding='utf-8')
js = (root / 'props.js').read_text(encoding='utf-8')
data = json.dumps(json.load(open(root / 'props_data.json', encoding='utf-8')), ensure_ascii=False, separators=(',', ':'))
data = data.replace('</', '<\\/')
assert '</script' not in js
out = src.replace('/*PROPS_JS*/', js, 1).replace('/*DATA_JSON*/', data, 1)
(here / 'index.html').write_text(out, encoding='utf-8')
print('index.html', len(out.encode('utf-8')), 'bytes')
