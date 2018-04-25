
from py2neo import Graph,Node,Relationship, NodeSelector
import re

with open('rmi_server_2.java') as f:
    content = f.read().splitlines()

save_content = content

#connect to graph
graph = Graph(password="test")
selector = NodeSelector(graph)
packages = []
classes = []
interfaces = []
methods_in_sequence = []

print("RMI Server Implementation uses : ")
for line in content:

    pattern = "java.rmi[.]?\w*"
    prog = re.compile(pattern)
    terms = line.split(" ")
    for term in terms:

        if prog.match(term):
            class_name = term.strip(';').split(".")[-1]
            class_node = selector.select("class", name=class_name).first()
            if class_node:
                classes.append(class_node)
                #print("Class : " + class_name)
            else:
                interface_name = term.strip(';').split(".")[-1]
                interface_node = selector.select("interface", name=interface_name).first()
                if interface_node:
                    interfaces.append(interface_node)
                    #print("Interface : " + interface_name)
            package_name_elements = term.strip(';').split(".")[:-1]
            package_name = ".".join(package_name_elements)
            package_node = selector.select("package", name=package_name).first()
            if package_node:
                if package_name not in packages:
                    packages.append(package_name)


for package in packages:
    print("Package : " + package)

count = 0
for line in save_content:
    method_pattern = "[^\(]*(\(.*\))[^\)]*"
    method_prog = re.compile(method_pattern)
    terms = line.split(" ")
    for term in terms:
        #print(term)
        if term.__contains__("."):
            parts = term.split(".")
            if(method_prog.match(parts[-1])):
                method_node = selector.select("method", name=parts[-1].split('(')[0]).first()

                if method_node:
                    for interface_node in interfaces:
                        #print(interface_node.properties['name'])
                        query = "MATCH (i:interface{name:'"+interface_node.properties['name']+"'})-" \
                                      "[r:CONTAINS_METHOD]->" \
                                      "(m:method{name:'"+method_node.properties['name']+"'}) RETURN m"
                        #relationship = graph.match_one(start_node=interface_node,rel_type='CONTAINS_METHOD',end_node=method_node,bidirectional= False)
                        method = graph.run(query).evaluate()
                        if(method):
                            print("Call from interface " + interface_node.properties['name'] + " -> " +method['name'])

                            m = Node('rmi_server_method', name = term, position_in_sequence = count,
                                     return_type = method['return_type'], signature = method['signature'])
                            graph.create(m)
                            methods_in_sequence.append(m)

                            count = count+1

                    for class_node in classes:
                        query = "MATCH (c:class{name:'"+class_node.properties['name']+"'})-" \
                                      "[r:CONTAINS_METHOD]->" \
                                      "(m:method{name:'"+method_node.properties['name']+"'}) RETURN m"
                        method = graph.run(query).evaluate()

                        if (method):
                            print(method['signature'])
                            print("Call from class " + class_node.properties['name'] + " -> " + method['name'])

                            m = Node('rmi_server_method', name=term, position_in_sequence = count,
                                     return_type=method['return_type'], signature=method['signature'])
                            graph.create(m)
                            methods_in_sequence.append(m)
                            count = count + 1

for index,methods in enumerate(methods_in_sequence):
    if index > 0:
        r = Relationship(methods_in_sequence[index-1], "THEN", methods_in_sequence[index])
        graph.create(r)