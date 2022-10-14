import os
import threading
from time import sleep
import requests

# Load balancer DNS name to use in the url
#LB_DNS_NAME = os.environ.get('LB_DNS_NAME')
LB_DNS_NAME = ""

CLUSTER1_PATH = '/cluster1'
CLUSTER2_PATH = '/cluster2'


def call_endpoint(path:str):
    '''
    Calls (GET request) the load balancer on the given path.
    @param path:str Path to call
    '''

    url = LB_DNS_NAME + path
    headers = {
        'content-type': 'application/json'
    }

    res = requests.get(url, headers=headers)

    print(f'Code : {res.status_code}, Text: {res.json()}')


def make_calls(nb:int, path:str):
    '''
    Make `nb` calls sequentially to `path`.
    @param nb:int number of calls to make
    @param path:str Path to call
    '''
    
    for i in range(nb):
        call_endpoint(path)
    

def first_thread_calls(path:str):
    '''
    First test function (will make the first test thread).
    @param path:str Path to call
    '''

    print("Started first test thread for path :", path)

    # 1000 GET requests sequentially
    make_calls(1000, path)

    print("Exited first test thread for path :", path)


def second_thread_calls(path:str):
    '''
    Second test function (will make the second test thread).
    @param path:str Path to call
    '''

    print("Started second test thread for path :", path)
    
    # 500 GET requests
    make_calls(500, path)

    # One minute sleep
    sleep(60)

    # 1000 GET requests
    make_calls(1000, path)

    print("Exited second test thread for path :", path)


def create_test_threads(path:str):
    '''
    This function creates the test threads needed given the path to call.
    @param path:str Path to call

    @returns test threads objects
    '''

    print("Creating test threads for path :", path)

    first_thread = threading.Thread(target=first_thread_calls, args=(path,))
    first_thread.start()

    second_thread = threading.Thread(target=second_thread_calls, args=(path,))
    second_thread.start()

    return first_thread, second_thread


if __name__ == '__main__':
    print("Starting Tests")
    make_calls(5, CLUSTER1_PATH)
    make_calls(5, CLUSTER2_PATH)

    # # Creating test threads for both clusters.
    # # We keep the threads to join them (make sure they end their execution) before shutdown.
    # threads = []
    # threads.extend(create_test_threads(CLUSTER1_PATH))
    # threads.extend(create_test_threads(CLUSTER2_PATH))

    # # Join all threads before exiting.
    # for thread in threads:
    #     thread.join()

    print("Completed tests!")