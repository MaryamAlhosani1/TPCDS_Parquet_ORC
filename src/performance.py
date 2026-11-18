import time

import pandas as pd

from common import TABLES, load_table, run_experiment


def performance_experiment(spark, scale, data, out, work, check_content):
    rows = []
    output_root = work / 'performance'
    output_root.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    destination = out / 'performance_results.csv'
    if destination.exists():
        destination.unlink()
    for table in TABLES:
        print(f'SF{scale} timings: {table}', flush=True)
        frame = load_table(spark, data, table)
        suffix = '_sf5' if scale == 5 else ''
        parquet_path = output_root / f'{table}.dat_parquet_perf{suffix}'
        orc_path = output_root / f'{table}.dat_orc_perf{suffix}'

        start = time.time()
        frame.write.mode('overwrite').option('compression', 'snappy').parquet(str(parquet_path))
        parquet_write_time = time.time() - start

        start = time.time()
        frame.write.mode('overwrite').option('compression', 'snappy').orc(str(orc_path))
        orc_write_time = time.time() - start

        start = time.time()
        spark.read.parquet(str(parquet_path)).count()
        parquet_read_time = time.time() - start

        start = time.time()
        spark.read.orc(str(orc_path)).count()
        orc_read_time = time.time() - start

        rows.append(dict(scale_factor=scale, table=table,
                         parquet_write_sec=round(parquet_write_time, 2),
                         orc_write_sec=round(orc_write_time, 2),
                         parquet_read_sec=round(parquet_read_time, 2),
                         orc_read_sec=round(orc_read_time, 2)))
    result = pd.DataFrame(rows)
    result.to_csv(destination, index=False, float_format='%.2f')
    return result


if __name__ == '__main__':
    run_experiment('performance', performance_experiment)
