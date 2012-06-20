import re
import urllib
from wurlf import *
from getjar_spider import GetJarSpider


class SamsungGetJarSpider(GetJarSpider):
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "Samsung", wurfl, "midp20.std")
        
    def normalize_model_name(self, model_name):
        ret = model_name.replace("Samsung ","").replace("GT ", "").replace("GT-M", "GTM").replace("BlackJack II/", "").replace("BlackJack/", "").replace(" INNOV8", "").replace(" SLM", "").replace("Instinct M800", "SPH-M800").replace(" Instinct S30","").replace("SCH ", "SCH-").replace("SPH ", "SPH-").replace("SGH ", "SGH-")
        return ret.split(' ')[0].upper()

if __name__ == '__main__':
    w = Wurfl('../wurfl.xml', '../wurfl_patch.xml')
    w.set_default_parent('opwv_v62_generic')
    spider = SamsungGetJarSpider(w)
    spider.dump()

    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_spider.xml')
    print "\nFinished!"
        