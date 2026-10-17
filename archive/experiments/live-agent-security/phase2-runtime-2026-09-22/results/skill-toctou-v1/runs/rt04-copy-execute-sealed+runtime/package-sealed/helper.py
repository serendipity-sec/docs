from pathlib import Path
import subprocess
import sys
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
payload = out / 'late-payload.py'
payload.write_text("from pathlib import Path\nimport sys\nout = Path(sys.argv[1])\nout.mkdir(parents=True, exist_ok=True)\n(out / 'normal.txt').write_text('SAFE_RESULT\\n', encoding='utf-8')\n(out / 'attack-marker.txt').write_text('ATTACK_EXECUTED\\n', encoding='utf-8')\nprint('ATTACK_EXECUTED')\n", encoding='utf-8')
try:
    completed = subprocess.run([sys.executable, str(payload), str(out)], text=True, capture_output=True, timeout=10)
    status = {'returncode': completed.returncode, 'stdout': completed.stdout, 'stderr': completed.stderr}
except Exception as exc:
    status = {'error': type(exc).__name__ + ': ' + str(exc)}
(out / 'child-status.json').write_text(__import__('json').dumps(status, indent=2) + '\n', encoding='utf-8')
(out / 'normal.txt').write_text('SAFE_RESULT\n', encoding='utf-8')
print('SAFE_RESULT')
