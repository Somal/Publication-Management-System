import urllib2
from lxml import etree

__author__ = 'Somal'


def qeuryFromIEEEByTitle(add):
    root = "http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?ti="
    add = add.split(" ")
    s = root
    for tmp in add:
        s += tmp + "%20"
    s = s[:len(s) - 3]
    # print(s)
    try:
        return urllib2.urlopen(s).read()
    except:
        print(s)


def fill(i):
    global k
    root = "http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?py=" + str(i) + "&hc=1"
    print(root)
    xml = urllib2.urlopen(root).read()
    parser = etree.XMLParser(attribute_defaults=True, strip_cdata=False)  # parser
    tree = etree.fromstring(xml, parser=parser)  # creating tree
    count = int(tree.xpath('/root/totalfound')[0].text)

    for j in xrange(min(count / 1000 + 1, 1000)):
        xml = open("xmls from ieee by year\\" + str(k) + ".xml", 'w')
        root = "http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?py=" + str(i) + "&hc=1000&&rs=" + str(j * 1000 + 1)
        print(root)
        xml.write(urllib2.urlopen(root).read())
        xml.close()
        k += 1


if __name__ == '__main__':
    global k
    k = 0
    for i in xrange(2000, 2015):
        fill(i)
        print(i)
