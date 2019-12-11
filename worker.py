# -*- coding: utf-8 -*-

from concurrent import futures
from types import FunctionType
from messages import welcome
import argparse
import sys
import worker_pb2_grpc
import worker_pb2
import grpc
import time
import collections
import ast
from multiprocessing import Process
from configuration import (
    worker_list,
    inverted_index_path,
    word_count_path,
    word_count_map,
    word_count_reducer,
    inverted_index_map,
    inverted_index_reducer,
    mapper_tasks_path,
    reducer_task_path,
    configuration_path,
)
import store_pb2
import store_pb2_grpc
import os
import pickle
# from data_store.server import init_data_store, connect_datastore, command_to_store
from constants import (
    INITIAL_STAGE,
    INTERMEDIATE_STAGE,
    FINAL_STAGE,
    TASK_INVERTED_INDEX,
    TASK_WORD_COUNT,
    DATA_STORE_PORT
)

from dependency_manager import Dependencies

log = Dependencies.log()

clusters = collections.defaultdict(list)
processes = collections.defaultdict(list)
stubs = collections.defaultdict(list)
store_stub = None
servers = []
store_stub = None


class WokerServicer(worker_pb2_grpc.WorkerServicer):

    def connect_to_store(self, request, context):
        connect_datastore(request.ip, request.port)
        response = worker_pb2.connection_response()
        response.data  = "1"
        return response
    
    def worker_map(self, request, context):
        #https://philip-trauner.me/blog/post/python-tips-dynamic-function-definition
        execCode = compile(request.map_function, "<string>", 'exec')
        map_func = FunctionType(execCode.co_consts[0], globals(), "foo")
        result = map_func(request.file_name, request.lines)
        response = worker_pb2.mapper_response()
        reponse_list = []
        tup = worker_pb2.tuple()
        for key,value in result:
            tup = worker_pb2.tuple()
            tup.key = key
            tup.value = value
            reponse_list.append(tup)
        response.result.extend(reponse_list)
        return response
    
    def worker_reducer(self, request, context):
        print('in reducer')
        response = worker_pb2.reducer_response()
        #https://philip-trauner.me/blog/post/python-tips-dynamic-function-definition
        execCode2 = compile(request.reducer_function, "string", 'exec')
        red_func = FunctionType(execCode2.co_consts[0], globals(), "foo") 
        result = red_func(list(request.result))
        print(result)
        for value, key in result.items():
            response.result.add(key = str(value), value= str(key))
        print(response)
        return response
    
    def ping(self, request, context):
        response = worker_pb2.ping_response()
        response.data = f"Yes I am listening on port {request.data}"
        return response

def connect_datastore(ip, port):
    global store_stub
    channel = grpc.insecure_channel(f'{ip}:{port}')
    store_stub =  store_pb2_grpc.GetSetStub(channel)
    log.write('Client channel established with the store', 'info')
    
def command_to_store(value, stage = INITIAL_STAGE):
    log.write('Making RPC call to store')
    global store_stub
    request = store_pb2.Request()
    request.operation = value
    request.stage = stage 
    response = store_stub.operation(request)
    return response.data


def ping_server(port, ip="127.0.0.1"):
    try:
        with grpc.insecure_channel(f"{ip}:{port}") as channel:
            stub = worker_pb2_grpc.WorkerStub(channel)
            request = worker_pb2.ping_request(data=port)
            response = stub.ping(request)
            log.write(response.data)
    except:
        log.write(f"Unable to ping to {ip}:{port}")

def save_initial_data(key, data):
    log.write(f"SAVE INITIAL DATA: Trying to store initial data from mapper {key}")
    command_to_store(f"set {key} {data}", INITIAL_STAGE)


def save_intermediate_data(key, data):
    log.write(f"SAVE INTERMEDIATE DATA: Trying to store initial data from mapper {key}")
    command_to_store(f"set {key} {data}", INTERMEDIATE_STAGE)


def save_final_data(key, data):
    log.write(f"SAVE FINAL DATA: Trying to store initial data from mapper {key}")
    command_to_store(f"set {key} {data}", FINAL_STAGE)



def convert_to_proto_format(list_of_tuples):

    response_list = []
    tup = worker_pb2.tuple()
    for key, value in list_of_tuples:
        tup = worker_pb2.tuple()
        tup.key = key
        tup.value = value
        response_list.append(tup)
    return response_list


def init_worker(port, cluster_id = 0):
    time.sleep(20)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    worker_pb2_grpc.add_WorkerServicer_to_server(
            WokerServicer(), server)
    
    
    failed = server.add_insecure_port(f'[::]:{port}')
    if failed != 0:
        server.start()
        log.write(f'Started Worker!. Listening on port {port}.', 'debug')
    else:
        log.write(f'Failed to start the worker', 'critical')

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

def main(port):
    
    global store_stub, servers

    log.write("Starting Worker", "info")

    # connect_datastore()
    init_worker(port, cluster_id = 0)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Worker for the map reduce')
    parser.add_argument("port", help="port for the worker", type=int)
    args = parser.parse_args()
    main(args.port)

