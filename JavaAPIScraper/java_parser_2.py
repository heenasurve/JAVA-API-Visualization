from py2neo import Graph,Node,Relationship, NodeSelector
import re
import sys
import plyj.parser
import plyj.model as m

files = ['rmi_server.java', 'rmi_client.java', 'rmi_server_interface.java']
graph = Graph(password="test")
selector = NodeSelector(graph)
p = plyj.parser.Parser()
roles = []

for file in files:
    with open(file) as f:
        content = f.read().splitlines()
    roles.append(file.split(".")[0])

print("Roles : ")
for role in roles:
    print(role)
print("\n\n")

for file in files:
    with open(file) as f:
        content = f.read().splitlines()
    roles.append(file.split(".")[0])

    save_content = content
    imports = []
    classes = []
    interfaces = []
    extends = []
    implements =[]
    types = []
    methods_in_sequence = []

    for line in content:

        pattern = "java.rmi[.]?\w*"
        prog = re.compile(pattern)
        terms = line.split(" ")
        for term in terms:
            if prog.match(term):
                imports.append(term)

    if len(imports)>0:
        print("Imports : ")
        for package in imports:
            print(package)

    tree = p.parse_file(file)


    for type_decl in tree.type_declarations:
        types.append(type_decl)
        if type(type_decl) is plyj.model.ClassDeclaration:
            classes.append(type_decl)
        if type(type_decl) is plyj.model.InterfaceDeclaration:
            interfaces.append(type_decl)

    if len(interfaces) > 0:
        print("Interfaces : ")
        for interface in interfaces:
            print(interface.name)

    if len(classes) > 0:
        print("Classes : ")
        for class_type in classes:
            print(class_type.name)

    for type_decl in tree.type_declarations:
        #print(type_decl.name)
        print(type_decl.extends)
        if type_decl.extends is not None:
            if type(type_decl.extends) is plyj.model.Type:
                #print(' -> extends ' + type_decl.extends.name.value)
                extends.append(type_decl.extends.name.value)
            else:
                if type(type_decl.extends) is list:
                    #print(' -> extends ' + type_decl.extends[0].name.value)
                    extends.append(type_decl.extends[0].name.value)
        if hasattr(type_decl, "implements") and len(type_decl.implements) is not 0:
            #print(' -> implements ' + ', '.join([type.name.value for type in type_decl.implements]))
            for interface_impl in type_decl.implements:
                implements.append(interface_impl.name.value)


    for extended_class in extends:
        print(' -> extends ' + extended_class)

    for impl_interface in implements:
        print(' -> implements ' + impl_interface)


    print("\n\n")