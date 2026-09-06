import os

static_dir = 'static'
data = {}
for root, dirs, files in os.walk(static_dir):
    for f in files:
        path = os.path.join(root, f)
        rel = os.path.relpath(path, static_dir).replace('\\', '/')
        with open(path, 'r', encoding='utf-8') as fh:
            data[rel] = fh.read()

with open('embedded_static.py', 'w', encoding='utf-8') as out:
    out.write('STATIC = {\n')
    for key, val in data.items():
        out.write('    %r: %r,\n' % (key, val))
    out.write('}\n')
print('written', len(data))
