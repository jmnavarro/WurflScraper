import re
import urllib
from wurlf import *
from getjar_spider import GetJarSpider


class LGGetJarSpider(GetJarSpider):
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "LG", wurfl, "midp20.lg")
        
    def normalize_model_name(self, model_name):
        ret = model_name.replace("LG ","").replace("LG-", "").replace(" Prada II", "").replace(" Rumor II", "").replace("Trax ", "")
        return ret.split(' ')[0].upper()

EXPRESSIONS = {
    'j2me_screen_width'          : [re.compile('Full Screen:\s*(\d*)\s*[xX]\s*\d*'), re.compile('Resolution:\s*(\d*)\s*[xX]\s*\d*')],
    'j2me_screen_height'         : [re.compile('Full Screen:\s*\d*\s*[xX]\s*(\d*)'), re.compile('Resolution:\s*\d*\s*[xX]\s*(\d*)')],
    'j2me_heap_size'             : [re.compile('Heap Size:\s*(\d*\s*[MK]B)')],
    'j2me_max_jar_size'          : [re.compile('Max. JAR Size:\s*(\d*\s*[MK]B)')],
    'j2me_max_record_store_size' : [re.compile('RMS Size:\s*(\d*\s*[MK]B)')],
    'j2me_cldc_1_0'              : [re.compile('CLDC\s*1\.0')],
    'j2me_cldc_1_1'              : [re.compile('CLDC\s*1\.1')],
    'j2me_midp_1_0'              : [re.compile('MIDP\s*1\.0')],
    'j2me_midp_2_0'              : [re.compile('MIDP\s*2\.0')],
    'j2me_midp_2_1'              : [re.compile('MIDP\s*2\.1')],
    'jsr_66'                     : [re.compile('JSR[-\s]66')],
    'jsr_75'                     : [re.compile('JSR[-\s]75')],
    'jsr_82'                     : [re.compile('JSR[-\s]82')],
    'jsr_120'                    : [re.compile('JSR[-\s]120')],
    'jsr_135'                    : [re.compile('JSR[-\s]135')],
    'jsr_169'                    : [re.compile('JSR[-\s]169')],
    'jsr_172'                    : [re.compile('JSR[-\s]172')],
    'jsr_177'                    : [re.compile('JSR[-\s]177')],
    'jsr_179'                    : [re.compile('JSR[-\s]179')],
    'jsr_180'                    : [re.compile('JSR[-\s]180')],
    'jsr_184'                    : [re.compile('JSR[-\s]184')],
    'jsr_185'                    : [re.compile('JSR[-\s]185')],
    'jsr_195'                    : [re.compile('JSR[-\s]195')],
    'jsr_205'                    : [re.compile('JSR[-\s]205')],
    'jsr_209'                    : [re.compile('JSR[-\s]209')],
    'jsr_211'                    : [re.compile('JSR[-\s]211')],
    'jsr_216'                    : [re.compile('JSR[-\s]216')],
    'jsr_217'                    : [re.compile('JSR[-\s]217')],
    'jsr_219'                    : [re.compile('JSR[-\s]219')],
    'jsr_226'                    : [re.compile('JSR[-\s]226')],
    'jsr_229'                    : [re.compile('JSR[-\s]229')],
    'jsr_234'                    : [re.compile('JSR[-\s]234')],
    'jsr_238'                    : [re.compile('JSR[-\s]238')],
    'jsr_239'                    : [re.compile('JSR[-\s]239')],
    'jsr_248'                    : [re.compile('JSR[-\s]248')],
    'jsr_256'                    : [re.compile('JSR[-\s]256')],
    'jsr_927'                    : [re.compile('JSR[-\s]927')]
}

max_devices = 0
current_device = 1


def get_capabilities(data):
    """ returns a map of capabilities and values """
    ret = {};
    for key in EXPRESSIONS.keys():
        for expr in EXPRESSIONS[key]:
            match = expr.search(data)
            if match:
                leng = len(match.groups())
                if leng >= 1:
                    ret[key] = match.group(leng)
                else:
                    ret[key] = 'true'
        if not ret.has_key(key):
            ret[key] = 'false'

    return ret
    

def load_device(model_tuple):
    global current_device
    global max_devices
    
    """ returns a map of capabilities and values """
    model_id = model_tuple[0]
    model_name = model_tuple[1]
    
    print "(%s/%s) Downloading %s..." % (current_device, max_devices, model_name)
    current_device += 1
    data = urllib.urlopen("http://developer.lgmobile.com/lge.mdn.pho.RetrievePhoneInfo.dev?modelName=" + model_id).read()

    ret = get_capabilities(data)
    ret["battlewizard_engine"] = "midp20.lg"

    return (model_tuple, ret)

       

def normalize(tuple):
    def normalize_capability_size(value):
        lv = value.lower()
        if value == 'false':
            value = '-2'
        elif lv.endswith('kb'):
            value = str(int(lv.split('kb')[0]) * 1024)
        elif lv.endswith('mb'):
            value = str(int(lv.split('mb')[0]) * 1024 * 1024)
            
        return value
    
    # normalize size
    caps = tuple[1]
    for cap in caps:
        if cap in ('j2me_max_jar_size', 'j2me_heap_size', 'j2me_max_record_store_size'):
            caps[cap] = normalize_capability_size(caps[cap])

            
""" Generate new devices depending on the name and the grouping made by manufacturer. 
For example:
    - "LX260 / LG260" becomes two devices: "LX260" and "LG260"
Once all devices are generated, those not existing in original wurfl.xml are removed 
"""
def duplicate_devices(tuples, w):
    def exists_device(devices, model):
        for d in devices:
            if d[1] == model:
                return True
        return False
    
    def duplicate_device(dev, devices, w, result):
        partial_res = []
        partial_res.append(dev)
        model_name = dev[1]
        if model_name.find(" / ") > -1:
            parts = model_name.split(" / ")
            partial_res.append((dev[0], parts[0]))
            partial_res.append((dev[0], parts[1]))

        # add only existing
        exists = False
        for new_dev in partial_res:
            model = new_dev[1]
            if w.exists_device("LG", model):
                result.append(new_dev)
                exists = True
                
        if not exists:
            # add all
            for new_dev in partial_res:
                result.append(new_dev)
           
    ret = []
    for d in tuples:
        duplicate_device(d, tuples, w, ret)
            
    return ret

    
def get_devices_list():
    def normalize_model_id(model):
        return model.replace(" / ", "+%2F+")
    
#    return [(normalize_model_id('LX260 / LG260', 'LG260')]
    
    PAGES = (1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121)
    ret = []
    expr = "<strong><a.*onclick=\"retrieveSubmit\('(.*)'\)\".*>(.*)</a></strong>"
    pattern = re.compile(expr)
    for p in PAGES:
        count = 0
        url = "http://developer.lgmobile.com/lge.mdn.pho.RetrievePhoneList.dev?modelName=&saveFileName=&categoryNum=1&specValue1=Java&specValue2=--------+Select+---------&specValue3=--------+Select+---------&pageSpec=undefined&targetRow="
        url += str(p)
        url += "&devonOrderBy=&sModelName=&andOr=and&mainSelect1=TECH%2CTECH&subSelect1=Java&mainSelect2=&subSelect2=&mainSelect3=&subSelect3="
        data = urllib.urlopen(url).read()
        match = pattern.search(data)
        while match:
            id = normalize_model_id(match.group(1))
            model = match.group(2)
            ret.append((id, model))
            count += 1
            match = pattern.search(data, match.end())
        print "page %s found %s" % (p, count)

    return ret


def get_devices(w):
    def remove_repeated(tuples):
        ret = []
        for d in tuples:
            if not d in ret:
                ret.append(d)
        return ret

    global max_devices
    
    """ returns a map of devices and capabilities xml"""
    devs = get_devices_list()
    devs = duplicate_devices(devs, w)
    devs = remove_repeated(devs)
    max_devices = len(devs)
    
    capabilities_tuples = map(load_device, devs)
    map(normalize, capabilities_tuples)
    
    #xml_tuples = map(get_patch, capabilities_tuples)

    return capabilities_tuples


if __name__ == '__main__':
    w = Wurfl('../wurfl.xml', '../wurfl_patch.xml')
    w.set_default_parent('lg_generic')
    tuples = get_devices(w)
#    tuples = []
    print "\nSetting devices..."
    for d in tuples:
        model_id = d[0][0]
        model_name = d[0][1]
        capabilities = d[1]
        capabilities["brand_name"] = 'LG'
        capabilities["model_name"] = model_name
        capabilities["j2me_data_source"] = "lg_spider"
        w.set_device(capabilities, None)
        
    # complete with getjar
    spider = LGGetJarSpider(w)
    spider.dump()

    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_spider.xml')
    print "\nFinished!"
        