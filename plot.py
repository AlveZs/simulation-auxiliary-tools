import glob
import os
import matplotlib.pyplot as plt
import pandas as pd

ROOT_FOLDER = './csv'
schedulers = []
csv_files = glob.glob(f'{ROOT_FOLDER}/*.csv')
GROUP_COLUMN = 'total_utilization'
X_LABEL = 'Utilization'
y_labels = ['Preemptions per job', 'Migrations per job']
metrics = ['preemptions_per_job', 'migrations_per_job']
markers = ['o', 'v', 's', 'D', 'X']
results_data_frames = []


for csv_file in csv_files:
    results_data_frames.append(pd.read_csv(csv_file))
    schedulers.append(os.path.basename(csv_file).split('.')[0])

pd.set_option("display.max.columns", None)

for n, metric in enumerate(metrics):
    ax = results_data_frames[0].groupby(GROUP_COLUMN)[metric].mean().plot(marker=markers[0])
    for i in range(1, len(results_data_frames)):
        results_data_frames[i].groupby(GROUP_COLUMN)[metric].mean().plot(ax=ax, marker=markers[i])

    ax.set(xlabel=X_LABEL, ylabel=y_labels[n])
    ax.legend(schedulers)

    plt.savefig(
        f"figures/{metric}.pdf",
        format='pdf',
        pad_inches=0,
        bbox_inches='tight'
    )
    plt.clf()
