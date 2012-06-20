import re
import urllib
from wurlf import *
from getjar_spider import GetJarSpider


class SiemensGetJarSpider(GetJarSpider):
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "Sagem", wurfl, "midp20.std")
        
    def include_device(self, model_id, model_name):
        return model_id.find('Vodafone') == -1
        
    def normalize_model_name(self, model_name):
        ret = model_name.replace("Sagem ", "").replace("MY  ","my").replace("MY ","my")
#        print "%s -> %s" % (model_name, ret)
        return ret
    

if __name__ == '__main__':
    w = Wurfl('../wurfl.xml', '../wurfl_patch.xml')
    w.set_default_parent('opwv_v61_generic')
    spider = SiemensGetJarSpider(w)
    spider.dump()

    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_spider.xml')
    print "\nFinished!"
