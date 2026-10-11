from pathlib import Path
import sys
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
(out / 'normal.txt').write_text('SAFE_RESULT\n', encoding='utf-8')
print('SAFE_RESULT')
