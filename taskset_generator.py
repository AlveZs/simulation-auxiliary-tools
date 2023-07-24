import json
import os
import xml.dom.minidom
from simso.generator.task_generator import (
    gen_randfixedsum,
    gen_periods_uniform,
    gen_tasksets,
    gen_arrivals
)
from configuration import Configuration

logs = []

def create_xml(duration, cycles_per_ms, scheduler, taskset_object):
    """
        Transforms a set of tasks in XML format.
    """
    xml_string = '<?xml version="1.0"  ?>'
    xml_string += (f'<simulation duration="{duration}" '
                    f'cycles_per_ms="{cycles_per_ms}" etm="wcet">')
    xml_string += ('<sched overhead="0" overhead_activate="0" overhead_terminate="0" '
                    f'class="simso.schedulers.{scheduler}"/>')
    xml_string += ('<caches memory_access_time="100"/>')
    xml_string += ('<processors>')
    for i in range(taskset_object["processors_number"]):
        xml_string += (f'<processor name="CPU {i + 1}" '
                        f'id="{i + 1}" '
                        'cl_overhead="0" cs_overhead="0" speed="1.0"/>'
        )
    xml_string += ('</processors>')
    xml_string += ('<tasks>')
    for task_id, task in enumerate(taskset_object["taskset"], start = 1):
        xml_string += (f'<task name="TASK T{task_id}" '
                    f'id="{task_id}" '
                    'task_type="Periodic" '
                    'abort_on_miss="yes" '
                    f'period="{task[1]}" '
                    'activationDate="0.0" '
                    'list_activation_dates="0" '
                    f'deadline="{task[1]}" '
                    'base_cpi="1.0" '
                    'instructions="0" '
                    'mix="0" '
                    f'WCET="{task[0]}" '
                    'ACET="0.0" '
                    'preemption_cost="0" '
                    'et_stddev="0.0" />')
    xml_string += '</tasks>'
    xml_string += '</simulation>'
    dom = xml.dom.minidom.parseString(xml_string)
    pretty_xml_as_string = dom.toprettyxml()
    with open('./failed-tasksets/xml/'
                f'{scheduler}-{(taskset_object["taskset_id"] - 1):04d}-' 
                f'{taskset_object["total_utilization"]}'
                f'U-{taskset_object["processors_number"]}'
                f'm-{taskset_object["tasks_number"]}n.xml''', 'w',
                encoding='UTF-8'
        ) as xml_file:
        xml_file.write(pretty_xml_as_string)


def create_custom_simulator_notation(taskset_id, taskset_object):
    """
        Transforms a set of tasks to a proprietary format.
    """
    root_folder = './tasksets/custom'
    with open(f'{root_folder}/{taskset_object["total_utilization"]}/'
                f'{taskset_id:04d}-'
                f'{taskset_object["total_utilization"]}U-'
                f'{taskset_object["processors_number"]}m-'
                f'{len(taskset_object["taskset"])}n.txt', 'w', encoding='UTF-8'
    ) as custom_simulator_file:
        custom_simulator_file.write(
            f'1 {taskset_object["processors_number"]} {taskset_object["tasks_number"]}\n'
        )
        for task in taskset_object["taskset"]:
            custom_simulator_file.write(
                f'1 '
                f'{" ".join([str(task[0]) for _ in range(taskset_object["processors_number"])])} '
                f'0 {task[1]} {task[1]} \n'
            )

def create_directories(target_utilization):
    """
        Creates the necessary directories to save the generated task sets files.
    """
    if not os.path.isdir('./tasksets'):
        os.makedirs('./tasksets/')
    if not os.path.isdir('./tasksets/custom'):
        os.makedirs('./tasksets/custom')
    if not os.path.isdir(f'./tasksets/{target_utilization}'):
        os.makedirs(f'./tasksets/{target_utilization}')
        os.makedirs(f'./tasksets/custom/{target_utilization}')

def generate(target_utilization, processors_number, tasks_number, initial_id = 1, rounds = 1000):
    """
        Generate a taskset.
    """
    duration_ms = Configuration.DURATION
    n_sporadic_tasks = 0

    general_info = {
        "taskset_id": 0,
        "processors_number": processors_number,
        "total_utilization": target_utilization,
        "min_period": Configuration.MIN_PERIOD, 
        "max_period": Configuration.MAX_PERIOD,
        "tasks_number": tasks_number,
        "taskset": [],
    }

    create_directories(target_utilization)

    for set_id in range(initial_id, initial_id + rounds):
        number_tasks =  tasks_number
        arrivals = []

        utilizations = gen_randfixedsum(
            1,
            target_utilization * processors_number,
            number_tasks
        )
        periods = gen_periods_uniform(
            number_tasks,
            1,
            Configuration.MIN_PERIOD,
            Configuration.MAX_PERIOD,
            round_to_int=True
        )

        taskset = gen_tasksets(utilizations, periods)[0]
        general_info["taskset_id"] = set_id + 1

        general_info["n_spor_tasks"] = n_sporadic_tasks

        for j in range(n_sporadic_tasks):
            arrivals.append(gen_arrivals(taskset[j][1], 0, duration_ms, True))

        general_info["arrivals"] = arrivals
        general_info["taskset"] =  taskset
        tasksets_json = json.dumps(general_info, indent=2)

        root_folder = './tasksets'
        with open(f'{root_folder}/{target_utilization}/'
                  f'{(set_id):04d}-'
                  f'{target_utilization}U-'
                  f'{processors_number}m-'
                  f'{number_tasks}n.json', 'w', encoding='UTF-8'
                ) as json_file:
            json_file.write(tasksets_json)
        create_custom_simulator_notation(set_id, general_info)

def generate_tasksets():
    """
        It creates sets of tasks according to
        the need for use, number of tasks and number of processors.
    """
    TASKSET_NUMBER = 1
    ROUNDS = 10
    target_utilizations = ['0.95', '0.96', '0.97', '0.98', '0.99']
    for tg_utilization in target_utilizations:
        for processors_quantity in range(3, 16):
            for tasks_quantity in range(
                processors_quantity + 1,
                3 * processors_quantity
            ):
                generate(
                    float(tg_utilization),
                    processors_quantity,
                    tasks_quantity,
                    initial_id=TASKSET_NUMBER,
                    rounds=ROUNDS
                )
                TASKSET_NUMBER += ROUNDS
                print(f'Done {Configuration.TOTAL_UTILIZATION}U {processors_quantity}m {tasks_quantity}n!')

def convert_json_to_xml(path, duration, cycles_per_ms, scheduler):
    """
        Converts a task set in JSON to XML.
    """
    with open(f'{path}', 'r', encoding='UTF-8') as json_file:
        tasksets_json = json.load(json_file)
        create_xml(
            duration,
            cycles_per_ms,
            scheduler,
            tasksets_json
        )
