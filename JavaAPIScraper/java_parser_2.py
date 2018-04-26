from py2neo import Graph,Node,Relationship, NodeSelector
import re
import sys
import plyj.parser
import plyj.model as m

files = ['rmi_server.java', 'rmi_client.java', 'rmi_server_interface.java']
descriptions = [
                'implements a remote object and registers it with the RMI registry',
                'looks up and invokes a remote object.',
                'provides the connection between the client and the server'
                ]
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
        if type_decl.extends is not None:
            if type(type_decl.extends) is plyj.model.Type:
                extends.append(type_decl.extends.name.value)
            else:
                if type(type_decl.extends) is list:
                    extends.append(type_decl.extends[0].name.value)
        if hasattr(type_decl, "implements") and len(type_decl.implements) is not 0:
            for interface_impl in type_decl.implements:
                implements.append(interface_impl.name.value)


    for extended_class in extends:
        print(' -> extends ' + extended_class)

    for impl_interface in implements:
        print(' -> implements ' + impl_interface)

    methods = []
    inner_statements = []
    for type_decl in tree.type_declarations:
        no_of_method_decls = 0
        index = 0
        for declaratn in type_decl.body:
            if type(declaratn) is m.MethodDeclaration:
                no_of_method_decls += 1

        for method_decl in [decl for decl in type_decl.body if type(decl) is m.MethodDeclaration]:
            param_strings = []
            for param in method_decl.parameters:
                if type(param.type) is str:
                    param_strings.append(param.type + ' ' + param.variable.name)
                else:
                    param_strings.append(param.type.name.value + ' ' + param.variable.name)
            methods.append(method_decl.name + '(' + ', '.join(param_strings) + ')')
            #print('    ' + method_decl.name + '(' + ', '.join(param_strings) + ')')

            if method_decl.body is not None:

                for statement in method_decl.body:
                    constructed_statement = ""
                    constructed_statement = "\n"
                    # assuming statements contained inside a block
                    if hasattr(statement, "block") and statement.block.statements is not None:
                        for stat in statement.block.statements:

                            if hasattr(stat, "result"):
                                constructed_statement += "return " + stat.result.value

                            # statment that declares a variable that holds the result of a function call
                            if type(stat) is plyj.model.VariableDeclaration:
                                variable_decl = stat.variable_declarators[0]
                                # variable declaration Type
                                constructed_statement += stat.type.name.value
                                # variable declaration - variable name
                                constructed_statement += " " + variable_decl.variable.name + " = "


                                if hasattr(variable_decl, "initializer"):

                                    # standard variable declaration
                                    if type(variable_decl.initializer) is plyj.model.Literal:
                                        constructed_statement += variable_decl.initializer.value + "\n"

                                    # an array access declaration
                                    if type(variable_decl.initializer) is plyj.model.ArrayAccess:
                                        initializer = variable_decl.initializer
                                        constructed_statement += initializer.target.value + "(" + initializer.index.value + ")" + "\n"

                                    # object creation statement
                                    if type(variable_decl.initializer) is plyj.model.InstanceCreation:
                                        initializer = variable_decl.initializer.type.name.value
                                        constructed_statement += "new " + initializer + "()" + "\n"

                                    # method_invocation_statement
                                    if type(variable_decl.initializer) is plyj.model.MethodInvocation:
                                        arguments = variable_decl.initializer.arguments
                                        constructed_statement += variable_decl.initializer.target.value + "." + variable_decl.initializer.name
                                        constructed_statement += "("
                                        for arg in arguments:
                                            constructed_statement += arg.value + ", "
                                        constructed_statement += ")" + "\n"

                                    if hasattr(variable_decl.initializer, "expression") and \
                                                    type(
                                                        variable_decl.initializer.expression) is plyj.model.MethodInvocation:
                                        expression = variable_decl.initializer.expression
                                        arguments = expression.arguments
                                        constructed_statement += expression.target.value + "." + expression.name
                                        constructed_statement += "("
                                        for arg in arguments:
                                            constructed_statement += arg.value + ", "
                                        constructed_statement += ")" + "\n"

                            # no variable holds the result of the method invocation
                            if type(stat) is plyj.model.MethodInvocation:
                                arguments = stat.type_arguments
                                constructed_statement += stat.target.value + "." + stat.name
                                constructed_statement += "("
                                for arg in arguments:
                                    constructed_statement += arg.value + ", "
                                constructed_statement += ")" + "\n"


                    # statement not contained in a block
                    else:
                        # plain return statement
                        stat = statement
                        if hasattr(stat, "result"):
                            constructed_statement += "return " + stat.result.value + "\n"

                        if type(stat) is plyj.model.VariableDeclaration:

                            variable_decl = stat.variable_declarators[0]
                            # variable declaration Type
                            constructed_statement += stat.type.name.value
                            # variable declaration - variable name
                            constructed_statement += " " + variable_decl.variable.name + " = "

                            if hasattr(variable_decl, "initializer"):
                                # standard variable declaration
                                if type(variable_decl.initializer) is plyj.model.Literal:
                                    constructed_statement += variable_decl.initializer.value + "\n"

                                # an array access declaration
                                if type(variable_decl.initializer) is plyj.model.ArrayAccess:
                                    initializer = variable_decl.initializer
                                    constructed_statement += initializer.target.value + "(" +initializer.index.value+ ")" + "\n"

                                # object creation statement
                                if type(variable_decl.initializer) is plyj.model.InstanceCreation:
                                    initializer = variable_decl.initializer.type.name.value
                                    constructed_statement += "new " + initializer + "()" + "\n"

                                # method_invocation_statement
                                if type(variable_decl.initializer) is plyj.model.MethodInvocation:
                                    arguments = variable_decl.initializer.arguments
                                    constructed_statement += variable_decl.initializer.target.value + "." + variable_decl.initializer.name
                                    constructed_statement += "("
                                    for arg in arguments:
                                        constructed_statement += arg.value + ", "
                                    constructed_statement += ")" + "\n"

                                if hasattr(variable_decl.initializer, "expression") and \
                                                type(
                                                    variable_decl.initializer.expression) is plyj.model.MethodInvocation:
                                    expression = variable_decl.initializer.expression
                                    arguments = expression.arguments
                                    constructed_statement += expression.target.value + "." + expression.name
                                    constructed_statement += "("
                                    for arg in arguments:
                                        constructed_statement += arg.value + ", "
                                    constructed_statement += ")" + "\n"

                        # # no variable holds the result of the method invocation
                        # if type(stat) is plyj.model.MethodInvocation:
                        #     # arguments = variable_decl.arguments
                        #     constructed_statement += stat.target.value + "." + stat.name
                        #     # constructed_statement += '[' + ', '.join(arguments) + ']'
                        #
                        # # variable decaration statement
                        # if type(statement) is plyj.model.VariableDeclaration:
                        #     variable_decl = statement.variable_declarators[0]
                        #     constructed_statement += statement.type.name.value + " "
                        #     constructed_statement += variable_decl.variable.name + " " + variable_decl.initializer
                        #
                        # # no variable holds the result of the method invocation
                        # if type(statement) is plyj.model.MethodInvocation:
                        #     expression = variable_decl.initializer.expression
                        #     arguments = expression.arguments
                        #     constructed_statement += expression.target.value + "." + expression.name
                        #     constructed_statement += '[' + ', '.join(arguments) + ']'
                        #     inner_method = Node("contained_statement",
                        #                         name=stat.target.value + "." + stat.name,
                        #                         arguments=expression.arguments
                        #                         )
                        #     graph.create(inner_method)
                        #     inner_statements.append(inner_method)
                    inner_statements.append(constructed_statement)

    for idx,method in enumerate(methods):
        print('  ' + "-> " + method)
        if len(inner_statements) > 0:
            print(inner_statements[idx] + "\n")

