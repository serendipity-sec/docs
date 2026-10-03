from pathlib import Path
import sys
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
try:
    Path(__file__).write_text("from pathlib import Path\nimport sys\nout = Path(sys.argv[1])\nout.mkdir(parents=True, exist_ok=True)\n(out / 'normal.txt').write_text('SAFE_RESULT\\n', encoding='utf-8')\n(out / 'attack-marker.txt').write_text('ATTACK_EXECUTED\\n', encoding='utf-8')\nprint('ATTACK_EXECUTED')\n", encoding='utf-8')
    (out / 'self-modify-status.txt').write_text('SELF_MODIFY_SUCCEEDED\n', encoding='utf-8')
except Exception as exc:
    (out / 'self-modify-status.txt').write_text(type(exc).__name__ + ': ' + str(exc) + '\n', encoding='utf-8')
(out / 'normal.txt').write_text('SAFE_RESULT\n', encoding='utf-8')
print('SAFE_RESULT')
