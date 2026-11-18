import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(script, *args):
    command = [sys.executable, '-u', str(ROOT / 'src' / script), *map(str, args)]
    print('\n' + ' '.join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--analysis-only', action='store_true')
    parser.add_argument('--check-content', action='store_true')
    parser.add_argument('--keep-data', action='store_true')
    args = parser.parse_args()
    if not args.analysis_only:
        extra = ['--check-content'] if args.check_content else []
        run('sequence.py', *extra)
        try:
            run('data_types.py', '--scale', 1, *extra)
            run('sensitivity.py', '--scale', 1, *extra)
        finally:
            if not args.keep_data:
                for scale in (1, 2, 5):
                    shutil.rmtree(ROOT / 'work' / 'data' / f'tpcds_sf{scale}', ignore_errors=True)
    run('statistical_analysis.py')
    run('performance_analysis.py')
    print('\nResults: results/ | Figures: figures/', flush=True)


if __name__ == '__main__':
    main()
