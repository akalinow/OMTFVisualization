# OMTFVisualization
Visualization of the CMS overlap muon track finder (OMTF) data and configuration.

First version of the code runs from a single python file.

The code requires input data with the probability density functions (pdf) in the XML format: Patterns.xml
After running once with the input Patterns.xml file, a numpy file is saved. Later tests can be made using
the numpy file, as this is much faster than s(suboptimal) XML parsing.
Additionaly for plotting the reconstruced events on top of pdf, a event data is needed: TestData.xml

Running the program:

./test.py