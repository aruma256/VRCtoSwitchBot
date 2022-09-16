from pathlib import Path

LANG_FILE = Path('vrctoswitchbot') / Path('lang.py')
LICENSE_FILE = Path('LICENSE')

with open(LANG_FILE, 'r', encoding='utf-8') as f:
    lang_string = f.read()

with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
    license_string = f.read()

lang_string = lang_string.replace(r'{LICENSE}', license_string)

with open(LANG_FILE, 'w', encoding='utf-8') as f:
    print(lang_string, file=f)
