# -*- coding: utf-8 -*-

configuration_path = 'worker_servers/configuration.py'
worker_list = [[('127.0.0.1', 50051), ('127.0.0.1', 50052), ('127.0.0.1', 50053), ('127.0.0.1', 50054),('127.0.0.1', 50055)], \
                [('127.0.0.1', 50056), ('127.0.0.1', 50057), ('127.0.0.1', 50058), ('127.0.0.1', 50059),('127.0.0.1', 50060)]]
word_count_path = './input_data/input.txt'
inverted_index_path = './input_data/dummy'
mapper_tasks_path = "./input_data/tasks/mapper/"
reducer_task_path = "./input_data/tasks/reducer/"





# ======================== MAP REDUCE FUNCTION PATHS ============================================
map_reduce_base_function_path = 'worker_servers/map_reduce_functions/'

word_count_map = f'{map_reduce_base_function_path}word_count_map.py'
word_count_reducer = f'{map_reduce_base_function_path}word_count_reducer.py'
inverted_index_map = f'{map_reduce_base_function_path}inverted_index_map.py'
inverted_index_reducer = f'{map_reduce_base_function_path}inverted_index_reducer.py'
# ======================== MPA REDUCE FUNCTION PATHS =============================================

