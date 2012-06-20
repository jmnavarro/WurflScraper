import re
import urllib
from wurlf import *
from getjar_spider import GetJarSpider


class HTCGetJarSpider(GetJarSpider):
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "HTC", wurfl, "midp20.alpha")
        
    def normalize_model_name(self, model_name):
        ret = model_name.replace("HTC ","").replace("MTeoR", "Breeze/MTeoR").replace("TyTN", "P4500/TyTN/Hermes").replace("Touch 3G", "Touch 3G T3232").replace("Touch HD", "Touch HD T8282")
        if ret[-1].islower():
            ret = ret.replace("/Pilgrim/Tilt", "").replace("P3650 Cruise", "Touch Cruise/P3650").replace("Touch Dual", "Touch Dual/P5500").replace("Touch Viva","HTC Touch Viva T2223")
#        print "%s -> %s" % (model_name, ret.upper())
        return ret


if __name__ == '__main__':
    w = Wurfl('../wurfl.xml', '../wurfl_patch.xml')
    w.set_default_parent('ms_mobile_browser_ver1_winmo5')
    spider = HTCGetJarSpider(w)
    spider.dump()

    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_spider.xml')
    print "\nFinished!"
        