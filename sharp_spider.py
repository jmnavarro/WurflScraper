import re
import urllib
from wurlf import *
from getjar_spider import GetJarSpider


class SharpGetJarSpider(GetJarSpider):
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "Sharp", wurfl, "midp20.sharp")
        
    def normalize_model_name(self, model_name):
        return model_name.replace("Sharp ","").replace("GX", "TQ-GX").replace("GXT", "GX-T").replace("TM", "TM-")
    
    def normalize_device_id(self, model_id, model_name):
        MAP = {'TQ-GX-L15' : 'sharp_tq_gxl15_ver1_sub',
               'TQ-GX-T15' : 'sharp_tq_gxt15_ver1_sub6232d1112'}

        if MAP.has_key(model_name):
            return MAP[model_name]
        else:
            return None


if __name__ == '__main__':
    w = Wurfl('../wurfl.xml', '../wurfl_patch.xml')
    w.set_default_parent('opwv_v7_generic')
    spider = SharpGetJarSpider(w)
    spider.dump()

    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_spider.xml')
    print "\nFinished!"
