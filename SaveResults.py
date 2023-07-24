import os
import csv

class SaveResults():
    """
        A class to produce a results file.
    """

    def __init__(self, target_folder):
        self.target_folder = target_folder
        self.rows = []
        self.csv_header = []
        self.initialize_output()

    def initialize_output(self):
        """
            Set the header of CSV results file.
        """
        self.csv_header = [
            "processors_number",
            "tasks_number",
            "sporadic_tasks",
            "total_utilization",
            "preemptions",
            "migrations",
            "preemptions_per_job",
            "system_preemption_per_job",
            "migrations_per_job",
            "system_migrations_per_job",
            "released_jobs",
            "deadlines_misses",
            "real_deadline_misses"
        ]

    def add_row(self, results, n_proc, total_utilization, n_tasks, n_periodic_tasks):
        """
            Add a row to CSV results file.
        """
        system_preemption_per_job = 0
        system_migrations_per_job = 0
        if results.total_released_jobs > 0:
            system_preemption_per_job = round(
                results.total_preemptions / results.total_released_jobs,
                2
            )
            system_migrations_per_job = round(
                results.total_migrations / results.total_released_jobs,
                2
            )
        self.rows.append(localize_floats([
            n_proc,
            n_tasks,
            n_tasks - n_periodic_tasks,
            total_utilization,
            results.total_preemptions,
            results.total_migrations,
            round(results.total_preemptions_per_job / n_tasks, 2),
            system_preemption_per_job,
            round(results.total_migrations_per_job / n_tasks, 2),
            system_migrations_per_job,
            results.total_released_jobs,
            results.total_exceeded_count,
            results.total_real_exceeded_count
        ]))

    def create_directories(self):
        """
            Create the necessary directories to save the results file.
        """
        if not os.path.isdir('./csv'):
            os.makedirs('./csv/')
        if not os.path.isdir(f'./csv/{self.target_folder}'):
            os.makedirs(f'./csv/{self.target_folder}')

    def save(self,  filename):
        """
            Save the CSV file with results.
        """
        self.create_directories()
        with open(f'./csv/{self.target_folder}/'
                  f'{filename}.csv',
                  'w', encoding='UTF-8', newline=''
            ) as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(self.csv_header)
            writer.writerows(self.rows)

def localize_floats(row):
    """
        Use comma as decimal separator.
    """
    return [
        str(el).replace('.', ',') if isinstance(el, float) else el
        for el in row
    ]
