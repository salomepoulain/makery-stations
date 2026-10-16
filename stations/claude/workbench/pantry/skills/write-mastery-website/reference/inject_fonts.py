import base64, sys, pathlib
import subprocess
d = pathlib.Path(subprocess.run(['kpsewhich', 'lmroman10-regular.otf'], capture_output=True, text=True).stdout.strip()).parent
faces = [('regular', 'normal', 'normal'), ('bold', 'bold', 'normal'), ('italic', 'normal', 'italic'), ('bolditalic', 'bold', 'italic')]
css = ''
for f, w, s in faces:
    b = base64.b64encode((d / f'lmroman10-{f}.otf').read_bytes()).decode()
    css += f'@font-face{{font-family:"LM Roman 10";src:url(data:font/otf;base64,{b}) format("opentype");font-weight:{w};font-style:{s};font-display:block}}\n'
src, out = sys.argv[1], sys.argv[2]
pathlib.Path(out).write_text(pathlib.Path(src).read_text().replace('/*FONTS*/', css))
