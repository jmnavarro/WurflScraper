import re
import urllib
from wurlf import *
from getjar_spider import GetJarSpider


class SiemensGetJarSpider(GetJarSpider):
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "Siemens", wurfl, "midp20.std")
        
    def include_device(self, model_id, model_name):
        return model_id != 'C65-Vodafone'

    def normalize_model_name(self, model_name):
        return model_name.replace("Siemens ","")
    
    
    
class BenQSiemensGetJarSpider(GetJarSpider):
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "BenQ-Siemens", wurfl, "midp20.std")
        
    def normalize_brand_name(self, brand_name):
        return "Siemens"
    
    

if __name__ == '__main__':
    w = Wurfl('../wurfl.xml', '../wurfl_patch.xml')
    w.set_default_parent('opwv_v61_generic')

    SiemensGetJarSpider(w).dump()
    BenQSiemensGetJarSpider(w).dump()
    

    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_spider.xml')
    print "\nFinished!"
