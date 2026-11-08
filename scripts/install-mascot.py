"""Install both guide and renderer into an agent's explicitly chosen skills folder."""
from pathlib import Path
import argparse,shutil,json
p=argparse.ArgumentParser();p.add_argument('--destination',required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[1];dest=Path(args.destination).expanduser().resolve()
names=['video-style-studio','mascot-video-guide']
for name in names:
 if not (root/'skills'/name/'SKILL.md').is_file():raise SystemExit(f'Incomplete source package: {name}')
 if (dest/name).exists():raise SystemExit(f'Preserving existing {dest/name}; choose a new destination or review an update explicitly.')
dest.mkdir(parents=True,exist_ok=True)
for name in names:shutil.copytree(root/'skills'/name,dest/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
print(json.dumps({'installed':[str(dest/n) for n in names],'dependencies_installed':False,'next':'Read mascot-video-guide/SKILL.md and run base doctor; dependencies require an explained plan.'},ensure_ascii=True))
