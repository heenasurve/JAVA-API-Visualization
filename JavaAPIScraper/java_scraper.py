from lxml import html
import requests
from py2neo import Graph,Node,Relationship

graph = Graph(password="your-db-password-goes-here")

page = requests.get("https://docs.oracle.com/javase/8/docs/api/overview-summary.html")
tree = html.fromstring(page.content)

packages = tree.xpath('//td/a/text()')
package_descriptions = tree.xpath('//td/div[@class="block"]/text()')

for package in packages:
    #print("/".join(package.split(".")))
    url = "https://docs.oracle.com/javase/8/docs/api/" + ("/".join(package.split("."))) + "/package-summary.html"
    package_page = requests.get(url)
    package_tree = html.fromstring(package_page.content)

    interfaces = package_tree.xpath('//td/a[contains(@title,"interface")]/text()')
    classes = package_tree.xpath('//td/a[contains(@title,"class")]/text()')

    p = Node("package", name=package)
    graph.create(p)

    for interface in interfaces:
        i = Node("interface", name=interface)
        graph.create(i)
        package_contains_interface = Relationship(p,"CONTAINS_INTERFACE",i)
        graph.create(package_contains_interface)

    for classname in classes:
        c = Node("class", name=classname)
        graph.create(c)
        package_contains_class = Relationship(p, "CONTAINS_CLASS", c)
        graph.create(package_contains_class)
