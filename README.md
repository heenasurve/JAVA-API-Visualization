# JAVA-API-Visualization

<html>
<body>
<h2 style="color=blue;">All JAVA SE 8 API packages, interfaces, classes and methods visualized in a graph database</h2>
<p>
  
<strong>Data Extraction</strong> - Scraping performed in Python using the requests and lxml libraries to write XPath expressions over the JAVA SE 8 API </p>
<p>
<strong>Data Visualization</strong> - Visualized using py2neo to construct the nodes and relationships in a Neo4j database </p>


<hr>
<h2> Data created so far: </h2>
<h3>Nodes: </h3>
<ul>
  <li>packages</li>
  <li>interfaces</li>
  <li>classes</li>
  <li>methods</li>
 </ul>
 
<h3>Relationships:</h3>
<ul>
  <li>package-[CONTAINS_INTERFACE]-interface</li>
  <li>package-[CONTAINS_CLASS]-class</li>
  <li>interface-[CONTAINS_METHOD]-method</li>
  <li>class-[CONTAINS_METHOD]-method</li>
  <li>method-[RETURNS]-class</li>
    OR
  <li>method-[RETURNS]-interface
</h3>


</body>
</html>
