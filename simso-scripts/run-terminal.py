#!/usr/bin/python3

"""
Example of a script that uses SimSo.
"""

import sys
from simso.core import Model
from simso.configuration import Configuration
from simso.utils.SchedLogger import sched_logger


def main(argv):
    if len(argv) == 2:
        # Configuration load from a file.
        configuration = Configuration(argv[1])
    else:
        # Manual configuration:
        configuration = Configuration()

        configuration.cycles_per_ms = 1000000
        configuration.duration = 20 * configuration.cycles_per_ms

        # Add tasks:
        configuration.add_task(name="T1", identifier=1, period=7,
                               activation_date=0, wcet=5, deadline=7)
        configuration.add_task(name="T2", identifier=2, period=7,
                               activation_date=0, wcet=5, deadline=7)
        configuration.add_task(name="T3", identifier=3, period=7,
                               activation_date=0, wcet=5, deadline=7)
        configuration.add_task(name="T4", identifier=4, period=7,
                               activation_date=0, wcet=5, deadline=7)
        configuration.add_task(name="T5", identifier=5, period=7,
                               activation_date=0, wcet=5, deadline=7)
        configuration.add_task(name="T6", identifier=6, period=7,
                               activation_date=0, wcet=5, deadline=7)
        configuration.add_task(name="T7", identifier=7, period=7,
                               activation_date=0, wcet=5, deadline=7)

        # Add a processor:
        configuration.add_processor(name="CPU 1", identifier=1)
        configuration.add_processor(name="CPU 2", identifier=2)
        configuration.add_processor(name="CPU 3", identifier=3)
        configuration.add_processor(name="CPU 4", identifier=4)
        configuration.add_processor(name="CPU 5", identifier=5)

        # Add a scheduler:
        #configuration.scheduler_info.filename = "../simso/schedulers/RM.py"
        configuration.scheduler_info.clas = "simso.schedulers.RUNPlus"

    # Check the config before trying to run it.
    configuration.check_all()

    # Init a model from the configuration.
    model = Model(configuration)

    # Execute the simulation.
    model.run_model()

    # Print logs.
    for log in model.logs:
        print(log)

    if len(sched_logger.rows) > 0 and len(argv) == 2 and argv[1]:
        sched_name = configuration.scheduler_info.clas.split(".")[-1]
        filename = argv[1].split(".")[0]
        sched_logger.save(f"{sched_name}-{filename}.txt")

    #print results
    print("TOTAL PREEMPTIONS", model.results.total_preemptions)
    print("TOTAL MIGRATIONS", model.results.total_migrations)
    print("TOTAL RELEASED JOBS", model.results.total_realeased_jobs)
    print("TOTAL EXCEEDED DEADLINES", model.results.total_exceeded_count)
    print("TOTAL REAL EXCEEDED DEADLINES", model.results.total_real_exceeded_count)

main(sys.argv)
