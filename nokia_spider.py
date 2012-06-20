import re
import urllib
from wurlf import *
from getjar_spider import GetJarSpider

GETJAR_EXPR = {
    'family'            : re.compile('User Interface.*S\d0 Edition.*:.*(S\d0 v\d)'),
    'release_year'      : re.compile('Production time.*:.*(\d{4}), \dQ</td>'),
    'j2me_heap_size'    : re.compile('Heap Size \(Bytes\)</font></b>:&nbsp;&nbsp;(\d*)</td></tr>'),
    'j2me_max_jar_size' : re.compile('Jar Size \(Bytes\)</font></b>:&nbsp;&nbsp;(\d*)</td></tr>'),
} 

class NokiaGetJarSpider(GetJarSpider):
    
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "Nokia", wurfl, None)
        
        
    def get_engine(self, model_id, model_name, capabilities):
        def get_bw_engine_by_family(family):
            ret = None
            is_old = family.endswith("1") or family.endswith("2")
            if is_old:
                is_s60 = family.startswith("S60")
                is_s40 = family.startswith("S40")
                if is_s40:
                    ret = "midp20.std"
                elif is_s60:
                    ret = "midp20.s60"
            else:
                ret = "midp20.alpha"
            return ret
        
        def get_bw_engine_by_date(year):
            y = int(year)
            if y <= 2005:
                ret = "midp20.std"
            else:
                ret = "midp20.alpha"
            return ret
        
        ret = "midp20.alpha"
        if capabilities.has_key("family") and capabilities["family"] != 'false':
            ret = get_bw_engine_by_family(capabilities["family"])
        else:
            print "    Family doesn't found for %s!" % model_name
            
        if not ret:
            if capabilities.has_key("release_year") and capabilities["release_year"] != 'false':
                ret = get_bw_engine_by_date(capabilities["release_year"])
            else:
                print "    Release year doesn't found for %s!" % model_name
                
            
        del capabilities["family"]
        del capabilities["release_year"]
            
        return ret
    
    
    def get_expressions(self):
        ret = GetJarSpider.get_expressions(self)
        ret.update(GETJAR_EXPR)
        return ret

    
    def normalize_model_name(self, model_name):
        ret = model_name.lstrip("Nokia ")
        # dirty hacks
        if ret == '3500':
            ret = '3500c' 
        return ret
    

    def normalize_capability_value(self, capability_name, value):
        ret = value
        if capability_name in ('j2me_heap_size', 'j2me_max_jar_size') and value == 'false':
            ret = None
        return ret
    


EXPRESSIONS = {
    'j2me_screen_width'  : re.compile('<dt>Screen Resolution</dt>\s*<dd>\s*(\d*) x \d*\s*</dd>'),
    'j2me_screen_height' : re.compile('<dt>Screen Resolution</dt>\s*<dd>\s*\d* x (\d*)\s*</dd>'),
    'j2me_cldc_1_0'      : re.compile('JSR 30 '),
    'j2me_cldc_1_1'      : re.compile('JSR 139 '),
    'j2me_nokia_ui'      : re.compile('Nokia UI API'),
    'j2me_midp_1_0'      : re.compile('JSR 37 '),
    'j2me_midp_2_0'      : re.compile('JSR 118 MIDP 2.0'),
    'j2me_midp_2_1'      : re.compile('JSR 118 MIDP 2.1'),
    'j2me_heap_size'     : re.compile('<dt>Maximum Heap Size</dt>\s*<dd>\s*(.*)\s*</dd>'),
    'j2me_max_jar_size'  : re.compile('<dt>Maximum JAR Size</dt>\s*<dd>\s*(.*)\s*</dd>'),
    'jsr_66'             : re.compile('JSR 66 '),
    'jsr_75'             : re.compile('JSR 75 '),
    'jsr_82'             : re.compile('JSR 82 '),
    'jsr_120'            : re.compile('JSR 120 '),
    'jsr_135'            : re.compile('JSR 135 '),
    'jsr_169'            : re.compile('JSR 169 '),
    'jsr_172'            : re.compile('JSR 172 '),
    'jsr_177'            : re.compile('JSR 177 '),
    'jsr_179'            : re.compile('JSR 179 '),
    'jsr_180'            : re.compile('JSR 180 '),
    'jsr_184'            : re.compile('JSR 184 '),
    'jsr_185'            : re.compile('JSR 185 '),
    'jsr_195'            : re.compile('JSR 195 '),
    'jsr_205'            : re.compile('JSR 205 '),
    'jsr_209'            : re.compile('JSR 209 '),
    'jsr_211'            : re.compile('JSR 211 '),
    'jsr_216'            : re.compile('JSR 216 '),
    'jsr_217'            : re.compile('JSR 217 '),
    'jsr_219'            : re.compile('JSR 219 '),
    'jsr_226'            : re.compile('JSR 226 '),
    'jsr_229'            : re.compile('JSR 229 '),
    'jsr_234'            : re.compile('JSR 234 '),
    'jsr_238'            : re.compile('JSR 238 '),
    'jsr_239'            : re.compile('JSR 239 '),
    'jsr_248'            : re.compile('JSR 248 '),
    'jsr_256'            : re.compile('JSR 256 '),
    'jsr_927'            : re.compile('JSR 927 '),
    'family'             : re.compile('<dt>Developer Platform</dt>\s*<dd>\s*<a href=".*">(.*)</a>\s*</dd>')
}

max_devices = 0
current_device = 1


def get_capabilities(data):
    """ returns a map of capabilities and values """
    ret = {};
    for key in EXPRESSIONS.keys():
        match = EXPRESSIONS[key].search(data)
        if match != None:
            if len(match.groups()) >= 1:
                ret[key] = match.group(1)
            else:
                ret[key] = 'true'
        else:
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
    data = urllib.urlopen("http://www.forum.nokia.com/Devices/Device_specifications/" + model_id).read()

    ret = get_capabilities(data)
    
    return (model_tuple, ret)

       

def normalize(tuple):
    def normalize_capability_size(value):
        if value == 'false':
            value = '-2'
        elif value.find("Unlimited") > -1:
        	value = '-1'
        elif value.find(' KB') > -1:
            value = str(int(value.split(' KB')[0]) * 1024)
        elif value.find(' MB') > -1:
            value = str(int(value.split(' MB')[0]) * 1024 * 1024)
        elif value.find(' bytes') > -1:
            value = str(int(value.split(' bytes')[0]))
        else:
            value = str(int(value))
        
        return value
    
    def normalize_battlewizard_engine(value):
        is_s60_old = value.startswith("S60 2nd Edition")
        is_s40_old = value.startswith("Series 40") and (value.find("1.0") > -1 or value.find("2.0") > -1 or value.find("1st Edition") > -1)
        if is_s40_old:
            ret = "midp20.std"
        elif is_s60_old:
            ret = "midp20.s60"
        else:
            ret = "midp20.alpha"

        return ret
    
    # normalize size
    caps = tuple[1]
    for cap in caps:
        if cap in ('j2me_max_jar_size', 'j2me_heap_size'):
            caps[cap] = normalize_capability_size(caps[cap])
        elif cap == "family":
            caps["battlewizard_engine"] = normalize_battlewizard_engine(caps[cap])
            del caps[cap]    

            

    
def get_devices_list():
#    return [('2330_classic', 'Nokia 2330 classic')]
#    return [('3220', 'Nokia 3220')]
#   return [('N97', 'Nokia N97')]

    data = urllib.urlopen("http://www.forum.nokia.com/devices/matrix_all_1.html").read()
    expr = '<option value="">Select Device</option>'
    pattern = re.compile(expr)
    match = pattern.search(data)
    
    expr = '<option value="/Devices/Device_specifications/([0-9a-zA-Z_-]*)">([0-9a-zA-Z -]*)</option>'
    pattern = re.compile(expr)
    ret = []
    while match:
        match = pattern.search(data, match.end())
        if match:
            ret.append(match.groups())

    return ret

def get_devices():
    global max_devices
    
    """ returns a map of devices and capabilities xml"""
    devs = get_devices_list()
    max_devices = len(devs)
    capabilities_tuples = map(load_device, devs)
    map(normalize, capabilities_tuples)
    
    #xml_tuples = map(get_patch, capabilities_tuples)

    return capabilities_tuples


if __name__ == '__main__':
    w = Wurfl('../wurfl.xml', '../wurfl_patch.xml')
    w.set_default_parent('nokia_generic')
#    tuples = []
    tuples = get_devices()
    print "\nSetting devices..."
    for d in tuples:
        model_id = d[0][0]
        model_name = d[0][1].split('Nokia ')[1]
        capabilities = d[1]
        capabilities["brand_name"] = 'Nokia'
        capabilities["model_name"] = model_name
        capabilities["j2me_data_source"] = "nokia_spider"
        w.set_device(capabilities, None)
        
    # complete with getjar
    spider = NokiaGetJarSpider(w)
    spider.dump()

    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_spider.xml')
    print "\nFinished!"
        