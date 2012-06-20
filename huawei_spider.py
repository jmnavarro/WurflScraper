import re
import urllib
from wurlf import *
from getjar_spider import GetJarSpider


class HuaweiGetJarSpider(GetJarSpider):
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "Huawei", wurfl, "midp20.std")
        

if __name__ == '__main__':
    w = Wurfl('../wurfl.xml', '../wurfl_patch.xml')
    w.set_default_parent('generic_xhtml')
    spider = HuaweiGetJarSpider(w)
    spider.dump()

    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_spider.xml')
    print "\nFinished!"
