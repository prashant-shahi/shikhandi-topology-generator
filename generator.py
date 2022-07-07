import argparse, json, uuid
from random import randrange

import constant

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s",'--service-count', type=int, required=True)
    parser.add_argument("-i",'--max-instance-count', type=int, default=3)
    parser.add_argument("-r",'--max-route-count', type=int, default=3)
    parser.add_argument("-a",'--max-attributesets-count', type=int, default=3)
    parser.add_argument("-e",'--max-eventsets-count', type=int, default=3)
    args = parser.parse_args()
    return vars(args)

def uuid4():
    return str(uuid.uuid4())

def writeToFile(content, filename="topology.json"):
    with open(filename, "w") as file:
        file.write(content)

def generateDownstreamCalls(routes):
    print(len(routes))

def generate(config):
    sc = config["service_count"]
    mic = config["max_instance_count"]
    mrc = config["max_route_count"]
    mra = config["max_attributesets_count"]
    mec = config["max_eventsets_count"]
    services = []
    serviceRoutes = {}
    for i in range(0, sc):
        instances = []
        for j in range(0,mic):
            instances.append(f'service-{i+1}-instance-{j+1}-{uuid4()}')
        attribute_sets = []
        for j in range(0,randrange(mra)+1):
            attribute_sets.append(constant.ATTRIBUTE_SETS[randrange(len(constant.ATTRIBUTE_SETS))])
        routes = []
        for j in range(0,randrange(mrc)+1):
            routes.append({
                "route": "",
                "maxLatencyMillis": randrange(50,1000)
            })
        serviceName = f'service-{i+1}-{uuid4()}'
        serviceRoutes.serviceName=routes.route
        services.append({
                "serviceName": serviceName,
                "instances": instances,
                "attributeSets": attribute_sets,
                "spanKind": "server", # TODO: change it to client/internal after signoz supports it
                "routes": routes
            })
        if i == 0: services[i]['eventSets'] = constant.EVENT_SETS
            
    writeToFile(json.dumps({"topology":{"services":services}}), "topology-test.json")

def main():
    config = argument_parser()
    if config["service_count"] < 1:
        print("service count passed should be more than one")
        exit()
    generate(config)

if __name__ == '__main__':
    main()
