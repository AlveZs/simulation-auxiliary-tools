import pandas as pd

SCHEDULER_NAME = 'RUN'
df = pd.read_csv(f'./merged/{SCHEDULER_NAME}.csv', index_col=0)
df = df.loc[(df['total_utilization'] <= 0.9) | (df['total_utilization'] == 1)]
(
    df.sort_values(by=['total_utilization', 'processors_number', 'tasks_number'])
        .reset_index(drop=True)
        .to_csv(f'./Filtered/{SCHEDULER_NAME}-Filtered.csv')
)
