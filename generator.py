import argparse
import json
import uuid
from random import randrange, sample

import constant

'''
This function parses the CLI arguments.
returns configurations dictionary with all CLI arguments.
'''
def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", '--service-count', type=int, required=True, help="Total number of services")
    parser.add_argument("-i", '--max-instance-count', type=int, default=3, help="Maximum number of instances")
    parser.add_argument("-r", '--max-route-count', type=int, default=3, help="Maximum number of routes")
    parser.add_argument("-d", '--max-downstreamcall_count', type=int, default=3, help="Maximum downstream calls count")
    parser.add_argument("-o", '--output-topology', type=str, default="topology.json", help="File to write the generated topology JSON")
    parser.add_argument('--console', action='store_true', help="Write generated topology JSON on console")
    args = parser.parse_args()
    return vars(args)

'''
This function generates random UUID.
returns random UUID (version 4) as string.
'''
def uuid4():
    return str(uuid.uuid4())

'''
This function takes string content and file name
content: JSON text to be written to file
filename: name of the JSON file.
'''
def write_to_file(content, filename):
    with open(filename, "w") as file:
        file.write(content)

'''
This function takes index of the root/parent node.

To make sure that we avoid cyclic traversal or random downstream calls,
let's assume services form a binary tree and traverse down
from a node to its children nodes.

list[(index-1)/2]	Returns the parent node
list[(2*index)+1]	Returns the left child node
list[(2*index)+2]	Returns the right child node

                      0
                      |
            |--------------------|
            1                    2
        |----------|         |----------|
        3          4         5          6
    |-------|  |------|  |------|   |-------|
    7       8  9     10  11     12  13      14

index: index of the root/parent service node, should be int
returns list of children indices of the service.
'''
def get_children(index):
    sc = config["service_count"]
    lc = 2*index+1
    rc = 2*index+2
    if index >= sc or lc >= sc or rc >= sc:
        return []
    return [lc] + get_children(lc) + [rc] + get_children(rc)

'''
This function takes service meta and index.
It generates random downstream calls with children service nodes.

services: list of all services
service_index: index of the service
returns list of all downstream calls.
'''
def generate_downstream_calls(services, service_index):
    childrens = get_children(service_index)
    mdc = min(len(childrens), config["max_downstreamcall_count"])
    if len(childrens) == 0:
        return {}
    if service_index == 0:
        downstream_call_sample = sample(childrens,mdc)
    else:
        downstream_call_sample = sample(childrens,randrange(1,mdc))
    downstream_calls = {}
    for i in downstream_call_sample:
        routes = services[i]['routes']
        for j in range(0, randrange(0, 3)):
            # services[i]: routes[randrange(0, len(routes))]
            downstream_calls[services[i]["serviceName"]]=routes[randrange(len(routes))]["route"]
    return downstream_calls

'''
This function generates all services with its data: instances,
routes, attribute sets, span kind and event sets.
'''
def generate():
    sc = config["service_count"]
    mic = config["max_instance_count"]
    mrc = config["max_route_count"]
    ot = config["output_topology"]
    regions_count = len(constant.REGIONS)
    attrsets_count = len(constant.ATTRIBUTE_SETS)

    services = []
    # generate services
    for i in range(0, sc):
        instances = []
        # generate instances
        for j in range(0, mic):
            instances.append(f'service-{i+1}-instance-{j+1}-{uuid4()}')
        routes = []
        # generate routes for first service (root route) and other services
        if i == 0:
            for j in range(0, mrc):
                route_name = f'/service-{i+1}-route-{j+1}-{uuid4()}'
                routes.append({
                    "route": route_name,
                    "maxLatencyMillis": randrange(1, 9)*100
                })
        else:
            for j in range(0, randrange(1, mrc)):
                route_name = f'/service-{i+1}-route-{j+1}-{uuid4()}'
                routes.append({
                    "route": route_name,
                    "maxLatencyMillis": randrange(1, 9)*100
                })

        # generate common attribute sets
        attribute_sets = [
            {
                "weight": randrange(1,100),
                "version": f'v{randrange(1,100)}',
            },
            {
                "weight": randrange(1,100),
                "region": constant.REGIONS[randrange(0,regions_count)],
            },
        ]
        # generate a random attribute set
        attribute_sets.append(constant.ATTRIBUTE_SETS[randrange(0,attrsets_count)])

        # append the service with all data
        service_name= f'service-{i+1}-{uuid4()}'
        services.append({
            "serviceName": service_name,
            "instances": instances,
            "attributeSets": attribute_sets,
            # TODO: change some of it to client/internal after the support
            "spanKind": "server",
            "routes": routes
        })

        # generate event sets for the first service (root node)
        if i == 0: services[i]['eventSets']= constant.EVENT_SETS

    for i in range(0, sc):
        routes_count = len(services[i]['routes'])
        for j in range(0, routes_count):
            services[i]['routes'][j]['downstreamCalls'] = generate_downstream_calls(services, i)

    root_routes = []
    initial_service_name = services[0]['serviceName']
    for route in services[0]['routes']:
        root_routes.append({
            "service": initial_service_name,
            "route": route['route'],
            "tracesPerHour": randrange(1, 10)*1000,
        })
    file_content = {
        "topology":{
            "services":services
        },
        "rootRoutes": root_routes
    }
    if config["console"]:
        print(json.dumps(file_content))
    else:
        write_to_file(json.dumps(file_content), ot)
        print('Topology JSON generated:', ot)
        print('*'*3,"DONE",'*'*3)


def main():
    global config
    config = argument_parser()
    if config["service_count"] < 3:
        print("service count passed should be more than two")
        exit(1)
    generate()


if __name__ == '__main__':
    main()
