import os

templates_dir = 'templates'
data = {}
for root, dirs, files in os.walk(templates_dir):
    for f in files:
        path = os.path.join(root, f)
        rel = os.path.relpath(path, templates_dir).replace('\\', '/')
        with open(path, 'r', encoding='utf-8') as fh:
            data[rel] = fh.read()

with open('embedded_templates.py', 'w', encoding='utf-8') as out:
    out.write('TEMPLATES = {\n')
    for key, val in data.items():
        out.write('    %r: %r,\n' % (key, val))
    out.write('}\n')
print('written', len(data))
