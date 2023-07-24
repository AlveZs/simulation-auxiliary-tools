import glob
import pandas as pd

SCHEDULER_NAME = 'NP'
root_folder = f'./to-merge/{SCHEDULER_NAME}'

csv_files = glob.glob(root_folder + '/*.csv')


df_concat = (
    pd.concat([pd.read_csv(f, decimal=',', sep=';') for f in csv_files ], ignore_index=True)
        .sort_values(by=['total_utilization', 'processors_number', 'tasks_number'])
        .reset_index(drop=True)
)

df_concat.to_csv(f'./merged/{SCHEDULER_NAME}.csv')
