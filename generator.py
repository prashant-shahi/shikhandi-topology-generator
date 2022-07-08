import argparse
import json
import uuid
from random import randrange, sample

import constant

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", '--service-count', type=int, required=True, help="Total number of services")
    parser.add_argument("-i", '--max-instance-count', type=int, default=3, help="Maximum number of instances")
    parser.add_argument("-r", '--max-route-count', type=int, default=3, help="Maximum number of routes")
    parser.add_argument("-a", '--max-attributesets-count', type=int, default=3, help="Maximum number of instance")
    parser.add_argument("-o", '--output-topology', type=str, default="topology.json", help="File to write the generated topology JSON")
    args = parser.parse_args()
    return vars(args)


def uuid4():
    return str(uuid.uuid4())


def write_to_file(content, filename):
    with open(filename, "w") as file:
        file.write(content)


def generate_downstream_calls(services, service_index, route_index):
    downstream_count = randrange(0,3)
    downstream_call_count = sample(range(0, config["service_count"]), downstream_count)
    downstream_calls = {}
    routes = services[service_index]['routes'][route_index]
    for i in downstream_call_count:
        routes = services[i]['routes']
        for j in range(0, randrange(0, 3)):
            # services[i]: routes[randrange(0, len(routes))]
            downstream_calls[services[i]["serviceName"]]=routes[randrange(len(routes))]["route"]
    return downstream_calls


def generate():
    sc = config["service_count"]
    mic = config["max_instance_count"]
    mrc = config["max_route_count"]
    ot = config["output_topology"]
    regions_count = len(constant.REGIONS)
    attrsets_count = len(constant.ATTRIBUTE_SETS)

    services = []
    for i in range(0, sc):
        instances = []
        for j in range(0, mic):
            instances.append(f'service-{i+1}-instance-{j+1}-{uuid4()}')
        routes = []
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
        attribute_sets.append(constant.ATTRIBUTE_SETS[randrange(0,attrsets_count)])
        service_name= f'service-{i+1}-{uuid4()}'
        services.append({
            "serviceName": service_name,
            "instances": instances,
            "attributeSets": attribute_sets,
            # TODO: change it to client/internal after the support
            "spanKind": "server",
            "routes": routes
        })

        if i == 0: services[i]['eventSets']= constant.EVENT_SETS

    for i in range(0, sc):
        routes_count = len(services[i]['routes'])
        for j in range(0, routes_count):
            services[i]['routes'][j]['downstreamCalls'] = generate_downstream_calls(services, i, j)

    root_routes = []
    initial_service_name = services[0]['serviceName']
    for route in services[0]['routes']:
        root_routes.append({
            "service": initial_service_name,
            "route": route['route'],
            "tracesPerHour": randrange(1, 150)*1000,
        })
    file_content = {
        "topology":{
            "services":services
        },
        "rootRoutes": root_routes
    }
    write_to_file(json.dumps(file_content), ot)
    print('*'*3,"DONE",'*'*3)


def main():
    global config
    config = argument_parser()
    if config["service_count"] < 3:
        print("service count passed should be more than two")
        exit()

    generate()


if __name__ == '__main__':
    main()
