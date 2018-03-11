from lxml import html
import sys
import requests
from py2neo import Graph,Node,Relationship, NodeSelector
from time import sleep

# connect to graph
graph = Graph(password="your-db-password-goes-here")
selector = NodeSelector(graph)

try:
    # get the Java SE 8 API docs
    page = requests.get("https://docs.oracle.com/javase/8/docs/api/overview-summary.html")
    # parse HTML page returned
    tree = html.fromstring(page.content)

    # get package names and descriptions
    packages = tree.xpath('//td/a/text()')
    package_descriptions = tree.xpath('//td/div[@class="block"]/text()')

    for package in packages:

        '''
        Construct URL for current package
        Get page from URL
        Parse HTML page
        Find interfaces and classes on the page
        '''
        url = "https://docs.oracle.com/javase/8/docs/api/" + ("/".join(package.split("."))) + "/package-summary.html"
        package_page = requests.get(url)
        package_tree = html.fromstring(package_page.content)

        interfaces = package_tree.xpath('//td/a[contains(@title,"interface")]/text()')
        classes = package_tree.xpath('//td/a[contains(@title,"class")]/text()')
        m_nodes = []

        # Create package nodes
        p = Node("package", name=package)
        graph.create(p)

        for interface in interfaces:
            '''
            For every interface in the package
                Create interface nodes
                Create package to interface relationships between the nodes
                Construct interface page URL
                Parse HTML returned to retrieve all interface methods
            '''
            i = Node("interface", name=interface)
            graph.create(i)
            package_contains_interface = Relationship(p,"CONTAINS_INTERFACE",i)
            graph.create(package_contains_interface)
            interface_url = "https://docs.oracle.com/javase/8/docs/api/" + ("/".join(package.split("."))) + "/" + interface + ".html"
            interface_page = requests.get(interface_url)
            interface_tree = html.fromstring(interface_page.content)
            interface_methods = interface_tree.xpath('//tr[@id]')

            #print(interface)
            for index,method in enumerate(interface_methods):
                '''
                For every interface method
                    Obtain method name, return type and arguments
                    Construct method signature
                    Create method node
                    Create a relationship from interface to interface methods
                '''
                str_index = str(index)
                ind = 0

                method_signature = ""
                return_type = ""

                method_return_type = interface_tree.xpath("//tr[@id='i"+str_index+"']/td[@class='colFirst']/code//text()")
                method_name = interface_tree.xpath("//tr[@id='i"+str_index+"']/td[@class='colLast']/code/span/a/text()")
                method_params = interface_tree.xpath("//tr[@id='i"+str_index+"']/td[@class='colLast']/code/a/text()")

                for text in method_return_type:
                   method_signature += text
                   return_type += text

                method_signature += "  "

                if(method_name):
                    if(not method_params):
                        method_params = interface_tree.xpath("//tr[@id='i"+str_index+"']/td[@class='colLast']/code/text()")
                        method_signature += method_name[0] + method_params[0]
                    else:
                        method_signature += method_name[0] + "("
                        for ind,param in enumerate(method_params):
                            if(ind < len(method_params)-1):
                                method_signature += method_params[ind] + ", "

                        method_signature += method_params[ind]
                        method_signature += ")"
                    print(method_signature)

                    im = Node("method", name=method_name[0], return_type = return_type, signature = method_signature)
                    graph.create(im)
                    m_nodes.append(im)
                    interface_contains_method = Relationship(i,"CONTAINS_METHOD",im)
                    graph.create(interface_contains_method)

        for classname in classes:
            '''
            For every class in the package
               Create class nodes
               Create package to class relationships between the nodes
               Construct class page URL
               Parse HTML returned to retrieve all class methods
            '''
            c = Node("class", name=classname)
            graph.create(c)
            package_contains_class = Relationship(p, "CONTAINS_CLASS", c)
            graph.create(package_contains_class)
            class_url = "https://docs.oracle.com/javase/8/docs/api/" + (
            "/".join(package.split("."))) + "/" + classname + ".html"

            class_page = requests.get(class_url)
            class_tree = html.fromstring(class_page.content)
            class_methods = class_tree.xpath('//tr[@id]')

            for index,method in enumerate(class_methods):
                '''
                For every class method
                   Obtain method name, return type and arguments
                   Construct method signature
                   Create method node
                   Create a relationship from class to class method
                '''
                str_index = str(index)
                ind = 0

                method_signature = ""
                return_type = ""

                method_return_type = class_tree.xpath("//tr[@id='i"+str_index+"']/td[@class='colFirst']/code//text()")
                method_name = class_tree.xpath("//tr[@id='i"+str_index+"']/td[@class='colLast']/code/span/a/text()")
                method_params = class_tree.xpath("//tr[@id='i"+str_index+"']/td[@class='colLast']/code/a/text()")

                for text in method_return_type:
                   method_signature += text
                   return_type += text

                method_signature += "  "

                if(method_name):
                    if(not method_params):
                        method_params = class_tree.xpath("//tr[@id='i"+str_index+"']/td[@class='colLast']/code/text()")
                        method_signature += method_name[0] + method_params[0]
                    else:
                        method_signature += method_name[0] + "("
                        for ind,param in enumerate(method_params):
                            if(ind < len(method_params)-1):
                                method_signature += method_params[ind] + ", "

                        method_signature += method_params[ind]
                        method_signature += ")"
                    print(method_signature)

                    cm = Node("method", name=method_name[0], return_type = return_type, signature = method_signature)
                    graph.create(cm)
                    m_nodes.append(cm)
                    class_contains_method = Relationship(c,"CONTAINS_METHOD",cm)
                    graph.create(class_contains_method)

        '''
        For every class/interface method
            if returned type is a class or interface instance
                Create a relationship between the method node to the class/interface node
        '''
        for method in m_nodes:
            class_node = selector.select("class", name=method.properties['return_type']).first()
            interface_node = selector.select("interface", name=method.properties['return_type']).first()
            if(class_node):
                print(class_node)
                method_returns_object = Relationship(method, "RETURNS", class_node)
                graph.create(method_returns_object)
            if(interface_node):
                print(interface_node)
                method_returns_object = Relationship(method, "RETURNS", interface_node)


except :
    print("Connection refused by the server..")
    print(sys.exc_info()[0])
    #trying again in 5 seconds
    sleep(5)
