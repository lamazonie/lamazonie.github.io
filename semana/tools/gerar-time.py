"""Gera semana/time/index.html a partir de semana/index.html (o template das creators).
Rodar sempre que o index.html mudar:  python3 semana/tools/gerar-time.py"""
import pathlib, re
root = pathlib.Path(__file__).resolve().parent.parent
s = (root / 'index.html').read_text(encoding='utf-8')
def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b)
rep('data-view="creators" data-base=""', 'data-view="time" data-base="../"')
rep("<title>Criativos da semana · L'Amazonie Studio</title>", '<title>Criativos da semana · Marketing e edição</title>')
s = re.sub(r'<meta property="og:[^>]*>\n', '', s)
rep('<a href="../creators.html" aria-label', '<a href="../" aria-label')
rep('src="brand/', 'src="../brand/')
rep('<span class="eyebrow">Studio · time de criação</span>', '<span class="eyebrow">Marketing e edição</span>')
rep('<a href="../creators.html">Voltar ao Studio</a>', '<a href="../">Ver a página das creators</a>')
(root / 'time' / 'index.html').write_text(s, encoding='utf-8')
print('time/index.html gerado')
