import argparse
import shutil

from common import ROOT, get_data, save_metadata, start_spark
from experiment import compression_experiment
from performance import performance_experiment


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-content', action='store_true')
    args = parser.parse_args()
    work = ROOT / 'work' / 'generated'
    spark = start_spark()
    sources = {}
    try:
        for scale in (1, 2, 5):
            data, commit = get_data(scale, ROOT / 'work' / 'data')
            sources[scale] = (data, commit)
            print(f'Compression SF{scale}', flush=True)
            out = ROOT / 'results' / f'compression_sf{scale}'
            save_metadata(spark, scale, commit, out, args.check_content)
            compression_experiment(spark, scale, data, out, work, args.check_content)

        for scale in (1, 2, 5):
            data, commit = sources[scale]
            print(f'Write and count timings SF{scale}', flush=True)
            out = ROOT / 'results' / f'performance_sf{scale}'
            save_metadata(spark, scale, commit, out, False)
            performance_experiment(spark, scale, data, out, work, False)
    finally:
        spark.stop()
        shutil.rmtree(work / 'performance', ignore_errors=True)


if __name__ == '__main__':
    main()
