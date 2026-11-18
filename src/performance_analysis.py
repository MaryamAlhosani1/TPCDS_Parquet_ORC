from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = {'customer', 'item', 'store', 'date_dim', 'store_sales'}
COLUMNS = ['scale_factor', 'table', 'parquet_write_sec', 'orc_write_sec',
           'parquet_read_sec', 'orc_read_sec']


def plot_metric(frame, parquet_col, orc_col, name, ylabel, maximum, ticks, legend):
    labels = [f'SF{scale}' for scale in frame.scale_factor]
    x = np.arange(len(frame))
    width = 0.32
    fig, ax = plt.subplots(figsize=(6.92, 3.72), dpi=300)
    fig.patch.set_facecolor('white')
    ax.bar(x - width / 2, frame[parquet_col], width,
           color='#304A63', edgecolor='#333333', linewidth=0.55, label='Parquet')
    ax.bar(x + width / 2, frame[orc_col], width,
           color='#E2E4E7', edgecolor='#333333', linewidth=0.55,
           hatch='////', label='ORC')
    ax.set_xticks(x, labels)
    ax.set_xlabel('Scale factor')
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, maximum)
    ax.set_yticks(ticks)
    ax.grid(axis='y', color='#D9D9D9', linewidth=0.6, alpha=0.65)
    ax.set_axisbelow(True)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.legend(loc=legend, frameon=False, ncol=1, handlelength=1.6,
              handletextpad=0.45, labelspacing=0.2, borderpad=0.15)
    fig.subplots_adjust(left=0.115, right=0.974, bottom=0.20, top=0.93)
    folder = ROOT / 'figures'
    folder.mkdir(parents=True, exist_ok=True)
    fig.savefig(folder / f'{name}.png', dpi=300, facecolor='white')
    fig.savefig(folder / f'{name}.svg', facecolor='white')
    plt.close(fig)


def analyze():
    frames = []
    for scale in (1, 2, 5):
        path = ROOT / 'results' / f'performance_sf{scale}' / 'performance_results.csv'
        frame = pd.read_csv(path)
        if list(frame.columns) != COLUMNS or len(frame) != 5 or set(frame.table) != TABLES:
            raise RuntimeError(f'Unexpected performance results schema: {path}')
        if (frame.scale_factor != scale).any():
            raise RuntimeError(f'Incorrect scale factor in {path}')
        if frame[COLUMNS[2:]].isnull().any().any() or frame[COLUMNS[2:]].lt(0).any().any():
            raise RuntimeError(f'Invalid timing values in {path}')
        frames.append(frame)
    measurements = pd.concat(frames, ignore_index=True)
    rows = []
    for scale, part in measurements.groupby('scale_factor', sort=True):
        sales = part.set_index('table').loc['store_sales']
        rows.append(dict(
            scale_factor=int(scale),
            parquet_total_write_sec=round(part.parquet_write_sec.sum(), 2),
            orc_total_write_sec=round(part.orc_write_sec.sum(), 2),
            parquet_store_sales_write_sec=sales.parquet_write_sec,
            orc_store_sales_write_sec=sales.orc_write_sec,
            store_sales_orc_write_saving_pct=round(100 * (
                sales.parquet_write_sec - sales.orc_write_sec) / sales.parquet_write_sec, 2),
            parquet_total_count_sec=round(part.parquet_read_sec.sum(), 2),
            orc_total_count_sec=round(part.orc_read_sec.sum(), 2)
        ))
    summary = pd.DataFrame(rows).sort_values('scale_factor')
    statistics = ROOT / 'results' / 'statistics'
    statistics.mkdir(parents=True, exist_ok=True)
    summary.to_csv(statistics / 'performance_summary.csv', index=False, float_format='%.2f')

    plt.rcParams.update({
        'font.family': 'Tinos', 'font.size': 10,
        'axes.labelsize': 11, 'xtick.labelsize': 10,
        'ytick.labelsize': 10, 'legend.fontsize': 10,
        'hatch.linewidth': 0.65, 'axes.edgecolor': '#333333',
        'axes.linewidth': 0.8, 'text.color': '#222222',
        'axes.labelcolor': '#222222', 'xtick.color': '#222222',
        'ytick.color': '#222222', 'savefig.facecolor': 'white',
        'svg.fonttype': 'none'
    })
    plot_metric(summary, 'parquet_total_write_sec', 'orc_total_write_sec',
                'fig07_write_time', 'Summed write-action time (s)',
                160, [0, 40, 80, 120, 160], 'upper left')
    plot_metric(summary, 'parquet_total_count_sec', 'orc_total_count_sec',
                'fig08_read_count_time', 'Summed read-and-count action time (s)',
                2.5, [0, .5, 1, 1.5, 2, 2.5], 'upper right')
    print('Performance summary and Figures 7-8 generated', flush=True)


if __name__ == '__main__':
    analyze()
