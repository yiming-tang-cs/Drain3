# SPDX-License-Identifier: MIT

import json
import logging
import sys
from os.path import dirname

from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
import os.path

# persistence_type = "NONE"
# persistence_type = "REDIS"
# persistence_type = "KAFKA"
persistence_type = "FILE"

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

if persistence_type == "KAFKA":
    from drain3.kafka_persistence import KafkaPersistence

    persistence = KafkaPersistence("drain3_state", bootstrap_servers="localhost:9092")

elif persistence_type == "FILE":
    from drain3.file_persistence import FilePersistence

    persistence = FilePersistence("drain3_state.bin")

elif persistence_type == "REDIS":
    from drain3.redis_persistence import RedisPersistence

    persistence = RedisPersistence(redis_host='',
                                   redis_port=25061,
                                   redis_db=0,
                                   redis_pass='',
                                   is_ssl=True,
                                   redis_key="drain3_state_key")
else:
    persistence = None

config = TemplateMinerConfig()
config.load(dirname(__file__) + "/drain3.ini")
config.profiling_enabled = False

template_miner = TemplateMiner(persistence, config)
print(f"Drain3 started with '{persistence_type}' persistence")
print(f"{len(config.masking_instructions)} masking instructions are in use")
# print(f"Starting training mode. Reading from std-in ('q' to finish)")

print("Please input log file path:")
file_path = input("> ")
while not os.path.exists(file_path):
    print("Invalid path. Please input log file path again:")
    file_path = input("> ")

###### create result file for printing
directory_path = file_path[0:file_path.rfind('/')]
result_file = open(directory_path + "/results.txt", "w")
id_results_file = open(directory_path + "/id_results.txt", "w")
print("Create result file: " + directory_path + "/results.txt")
print("Create result file: " + directory_path + "/id_results.txt")

##### read file content
file = open(file_path, "r")
log_lines = file.readlines()

original_stdout = sys.stdout
sys.stdout = result_file

for log_line in log_lines:
    result = template_miner.add_log_message(log_line)
    result_json = json.dumps(result)
    # print(result_json)
    cluster_id = json.loads(result_json)["cluster_id"]
    print("Cluster: ", end = '')
    print(cluster_id)
    print(result_json)
    print("-----------------------------------------------")
    id_results_file.write(str(cluster_id) + "\n")
    # template = result["template_mined"]
    # params = template_miner.extract_parameters(template, log_line)
    # print("Parameters: " + str(params))

# print("Training done. Mined clusters:")
# for cluster in template_miner.drain.clusters:
#     print(cluster)

sys.stdout = original_stdout

file.close()
result_file.close()
id_results_file.close()

# Not using for now
# print(f"Starting inference mode, matching to pre-trained clusters. Input log lines or 'q' to finish")
# while True:
#     log_line = input("> ")
#     if log_line == 'q':
#         break
#     cluster = template_miner.match(log_line)
#     if cluster is None:
#         print(f"No match found")
#     else:
#         template = cluster.get_template()
#         print(f"Matched template #{cluster.cluster_id}: {template}")
#         print(f"Parameters: {template_miner.get_parameter_list(template, log_line)}")
