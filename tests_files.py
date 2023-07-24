import sys
import json
import time
from simso.core import Model
from simso.configuration import Configuration
from SaveResults import SaveResults
from os import listdir
from datetime import timedelta

from taskset_generator import convert_json_to_xml

logs = []

def generate_tasks(configuration, taskset, n_sporadic_tasks, arrivals):
    """
        Instantiate the tasks to run the simulation.
    """
    for n, (ci, pi) in enumerate(taskset):
        if n < n_sporadic_tasks:
            configuration.add_task(
                "Task " + str(n), n, period=pi, wcet=ci, deadline=pi,
                task_type="Sporadic",
                list_activation_dates=arrivals[n])
        else:
            configuration.add_task("Task " + str(n), n, period=pi, wcet=ci, deadline=pi)

def simulate():
    """
        Simulate sets of tasks in a folder, saving the result as a csv file.
    """
    start = time.time()
    root_folder = './tasksets10'
    utilizations_folders = ['1']
    scheduler_class = "simso.schedulers.RUN"
    scheduler_name = scheduler_class.split(".")[-1]
    total_utilization = 0
    for folder in utilizations_folders:
        tasksets_files = listdir(f'{root_folder}/{folder}')
        files_quantity = len(tasksets_files)
        save_results = SaveResults(scheduler_name)
        for file_id, file in enumerate(tasksets_files, start=1):
            with open(f'{root_folder}/{folder}/{file}', 'r', encoding='UTF-8') as json_file:
                tasksets_json = json.load(json_file)
                n_proc = tasksets_json["processors_number"]
                n_tasks = tasksets_json["tasks_number"]
                total_utilization = tasksets_json["total_utilization"]
                configuration = Configuration()
                n_spor_tasks = tasksets_json["n_spor_tasks"]
                n_per_tasks = n_tasks - n_spor_tasks

                configuration.cycles_per_ms = 10000
                configuration.duration = 1000 * configuration.cycles_per_ms
                generate_tasks(
                    configuration,
                    tasksets_json["taskset"],
                    n_spor_tasks,
                    tasksets_json["arrivals"]
                )
                for i in range(n_proc):
                    configuration.add_processor(name=f'CPU {i}', identifier=i)

                configuration.scheduler_info.clas = scheduler_class
                # configuration.scheduler_info.data = { "K": n_proc }
                configuration.check_all()

                # Init a model from the configuration.
                model = Model(configuration)
                model.run_model()
                save_results.add_row(model.results, n_proc, total_utilization, n_tasks, n_per_tasks)
                if model.results.total_real_exceeded_count > 0:
                    print("FATAL ERROR")
                    print(model.results.total_real_exceeded_count)
                    convert_json_to_xml(
                        f'{root_folder}/{folder}/{file}',
                        configuration.duration,
                        configuration.cycles_per_ms,
                        scheduler_name
                    )
                print(f'{scheduler_name} - {total_utilization}U - '
                    f'{file_id}/{files_quantity} - '
                    f'{round((file_id/files_quantity) * 100, 1)}%'
                )
        save_results.save(f'{total_utilization}')
        end = time.time()
        print(f'Elapsed time: {str(timedelta(seconds = end - start))}')

simulate()
