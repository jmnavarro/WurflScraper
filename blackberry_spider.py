from wurlf import Wurfl
from getjar_spider import GetJarSpider

class BlackBerryGetJarSpider(GetJarSpider):
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "BlackBerry", wurfl, "midp20.blackberry")
        
    def normalize_brand_name(self, brand_name):
        return "RIM"

    def normalize_model_name(self, model_name):
        return "BlackBerry %s" % model_name.replace("Tour","").replace("Bold","").replace("Storm","").replace(" ", "")


if __name__ == '__main__':
    w = Wurfl('../wurfl.xml', '../wurfl_patch.xml')
    w.set_default_parent('blackberry_generic')
    spider = BlackBerryGetJarSpider(w)
    spider.dump()

    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_spider.xml')
    print "\nFinished!"

