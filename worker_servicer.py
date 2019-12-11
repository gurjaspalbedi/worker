# -*- coding: utf-8 -*-
import worker_pb2
import worker_pb2_grpc
from types import FunctionType

class WokerServicer(worker_pb2_grpc.WorkerServicer):
    
    def worker_map(self, request, context):
        print('in mapper')
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