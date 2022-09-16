from pathlib import Path
import subprocess

# replace about

LANG_FILE = Path('vrctoswitchbot') / Path('lang.py')
LICENSE_FILE = Path('LICENSE')

with open(LANG_FILE, 'r', encoding='utf-8') as f:
    lang_code = f.read()

with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
    license_string = f.read()

lang_code = lang_code.replace(r'{LICENSE}', license_string)

# replace lib license strings

proc = subprocess.run('pip-licenses -f plain-vertical -a -l --no-license-path'.split(),
                      check=True, capture_output=True)

lang_code = lang_code.replace(r'{OSS_LICENSE}', proc.stdout.decode())

with open(LANG_FILE, 'w', encoding='utf-8') as f:
    print(lang_code, file=f)
