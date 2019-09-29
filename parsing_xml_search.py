import xml.etree.ElementTree as ET
tree = ET.parse('query.xml')
root = tree.getroot()

# all items data
print('Expertise Data:')

for elem in root:
   for subelem in elem:
      print(subelem.text)