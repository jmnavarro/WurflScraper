import re
import urllib
from wurlf import *
from getjar_spider import GetJarSpider


class SonyEricssonGetJarSpider(GetJarSpider):
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "Sony-Ericsson", wurfl, "midp20.std")
        
    def normalize_brand_name(self, brand_name):
        return "SonyEricsson"
    
    def normalize_devices_list(self, devices):
        def duplicate_device(dev, result):
            def exists_device(dev_list, model):
                for d in dev_list:
                    if d[1] == model:
                        return True
                return False
            
            partial_res = []
            partial_res.append(dev)
            model_name = dev[1]
            
            add_suffix = len(model_name) in (4,5) and model_name[0].isalpha() and model_name[1].isdigit()
            if add_suffix:
                current_suffix = model_name[-1]
                if current_suffix.isdigit() or not model_name[-2].isdigit():
                    current_suffix = ''
                for letter in ('i', 'a', 'c'):
                    if letter != current_suffix or current_suffix == '':
                        if current_suffix == '':
                            model_name = dev[1] + letter
                        else:
                            model_name = dev[1].rstrip(current_suffix) + letter
                        if not exists_device(devices, model_name) and not exists_device(result, model_name):
                            partial_res.append((dev[0], model_name))
    
            # add only existing
            exists = False
            for new_dev in partial_res:
                model = new_dev[1]
                if self.wurfl.exists_device("SonyEricsson", model):
                    result.append(new_dev)
                    exists = True
                    
            if not exists:
                # add all
                for new_dev in partial_res:
                    result.append(new_dev)
               
        ret = []
        for d in devices:
            duplicate_device(d, ret)
                
        return ret


EXPRESSIONS = {
    'j2me_screen_width'  : re.compile('<h5>\s*Screen Sizes\s*</h5>\s*<p>\s*(\d*)[xX]\d*\s*</p>'),
    'j2me_screen_height' : re.compile('<h5>\s*Screen Sizes\s*</h5>\s*<p>\s*\d*[xX](\d*)\s*</p>')
}

ALTERNATIVE_EXPRESSIONS = {
    'j2me_cldc_1_0'      : re.compile('<li>\s*CLDC 1.0\s*</li>'),
    'j2me_cldc_1_1'      : re.compile('<li>\s*CLDC 1.0\s*</li>'),
    'j2me_nokia_ui'      : re.compile('<li>\s*Nokia UI API [\d\.]*\s*</li>'),
    'j2me_midp_1_0'      : re.compile('<li>\s*CLDC 1.0\s*</li>'),
    'j2me_midp_2_0'      : re.compile('<li>\s*CLDC 1.1\s*</li>'),
    'j2me_midp_2_1'      : re.compile('<li>\s*MIDP 2.1\(JSR 118\)\s*</li>'),
    'jsr_66'             : re.compile('<li>\s*.*\(JSR[- ]66\)\s*</li>'),
    'jsr_75'             : re.compile('<li>\s*.*\(JSR[- ]75\)\s*</li>'),
    'jsr_82'             : re.compile('<li>\s*.*\(JSR[- ]82\)\s*</li>'),
    'jsr_120'            : re.compile('<li>\s*.*\(JSR[- ]120\)\s*</li>'),
    'jsr_135'            : re.compile('<li>\s*.*\(JSR[- ]135\)\s*</li>'),
    'jsr_169'            : re.compile('<li>\s*.*\(JSR[- ]169\)\s*</li>'),
    'jsr_172'            : re.compile('<li>\s*.*\(JSR[- ]172\)\s*</li>'),
    'jsr_177'            : re.compile('<li>\s*.*\(JSR[- ]177\)\s*</li>'),
    'jsr_179'            : re.compile('<li>\s*.*\(JSR[- ]179\)\s*</li>'),
    'jsr_180'            : re.compile('<li>\s*.*\(JSR[- ]180\)\s*</li>'),
    'jsr_184'            : re.compile('<li>\s*.*\(JSR[- ]184\)\s*</li>'),
    'jsr_185'            : re.compile('<li>\s*.*\(JSR[- ]185\)\s*</li>'),
    'jsr_195'            : re.compile('<li>\s*.*\(JSR[- ]195\)\s*</li>'),
    'jsr_205'            : re.compile('<li>\s*.*\(JSR[- ]205\)\s*</li>'),
    'jsr_209'            : re.compile('<li>\s*.*\(JSR[- ]209\)\s*</li>'),
    'jsr_211'            : re.compile('<li>\s*.*\(JSR[- ]211\)\s*</li>'),
    'jsr_216'            : re.compile('<li>\s*.*\(JSR[- ]216\)\s*</li>'),
    'jsr_217'            : re.compile('<li>\s*.*\(JSR[- ]217\)\s*</li>'),
    'jsr_219'            : re.compile('<li>\s*.*\(JSR[- ]219\)\s*</li>'),
    'jsr_226'            : re.compile('<li>\s*.*\(JSR[- ]226\)\s*</li>'),
    'jsr_229'            : re.compile('<li>\s*.*\(JSR[- ]229\)\s*</li>'),
    'jsr_234'            : re.compile('<li>\s*.*\(JSR[- ]234\)\s*</li>'),
    'jsr_238'            : re.compile('<li>\s*.*\(JSR[- ]238\)\s*</li>'),
    'jsr_239'            : re.compile('<li>\s*.*\(JSR[- ]239\)\s*</li>'),
    'jsr_248'            : re.compile('<li>\s*.*\(JSR[- ]248\)\s*</li>'),
    'jsr_256'            : re.compile('<li>\s*.*\(JSR[- ]256\)\s*</li>'),
    'jsr_927'            : re.compile('<li>\s*.*\(JSR[- ]927\)\s*</li>')
}


#http://developer.sonyericsson.com/getDocument.do?docId=97267
PLATFORMS = {
    0: {
            'j2me_cldc_1_0'      : "false",
            'j2me_cldc_1_1'      : "false",
            'j2me_nokia_ui'      : "false",
            'j2me_midp_1_0'      : "false",
            'j2me_midp_2_0'      : "false",
            'j2me_midp_2_1'      : "false",
            'jsr_66'             : "false",
            'jsr_75'             : "false",
            'jsr_82'             : "false",
            'jsr_120'            : "false",
            'jsr_135'            : "false",
            'jsr_169'            : "false",
            'jsr_172'            : "false",
            'jsr_177'            : "false",
            'jsr_179'            : "false",
            'jsr_180'            : "false",
            'jsr_184'            : "false",
            'jsr_185'            : "false",
            'jsr_195'            : "false",
            'jsr_205'            : "false",
            'jsr_209'            : "false",
            'jsr_211'            : "false",
            'jsr_216'            : "false",
            'jsr_217'            : "false",
            'jsr_219'            : "false",
            'jsr_226'            : "false",
            'jsr_229'            : "false",
            'jsr_234'            : "false",
            'jsr_238'            : "false",
            'jsr_239'            : "false",
            'jsr_248'            : "false",
            'jsr_256'            : "false",
            'jsr_927'            : "false"
       },
    1: {
            'j2me_cldc_1_0'      : "true",
            'j2me_midp_1_0'      : "true",
            'jsr_120'            : "true",
            'jsr_135'            : "true"
       },
    2: {
            'j2me_cldc_1_1'      : "true",
            'j2me_nokia_ui'      : "true",
            'j2me_midp_2_0'      : "true",
            'jsr_185'            : "true"
       },
    3: {
            'jsr_184'            : "true"
       },
    4: {
       },
    5: {
            'jsr_75'             : "true",
            'jsr_82'             : "true"
       },
    6: {
            'jsr_172'            : "true",
            'jsr_205'            : "true",
       },
    7: {
            'jsr_234'            : "true"
       },
    8: {
            'jsr_177'            : "true",
            'jsr_179'            : "true",
            'jsr_180'            : "true",
            'jsr_211'            : "true",
            'jsr_226'            : "true",
            'jsr_229'            : "true",
            'jsr_234'            : "true",
            'jsr_238'            : "true",
            'jsr_239'            : "true",
            'jsr_248'            : "true",
            'jsr_256'            : "true"
       },
       
          
}

max_devices = 0
current_device = 1


def extract_capabilities_by_expressions(data, ret, expressions, overwrite):
    def set_val(k, v):
        if overwrite or not ret.has_key(k):
            ret[k] = v
            
    for key in expressions.keys():
        match = expressions[key].search(data)
        if match != None:
            if len(match.groups()) >= 1:
                set_val(key, match.group(1))
            else:
                set_val(key, 'true')
        else:
            set_val(key, 'false')


def clone_dict(origen, destino):
    for k in origen:
        destino[k] = origen[k]
    return destino


def extract_capabilities_by_platform(data, result):
    ret = True
    expr = re.compile("<h5>\s*Platforms\s*</h5>[\w\s<>\d]*Java Platform (\d)")
    match = expr.search(data)
    if match != None and len(match.groups()) >= 1:
        plat = int(match.group(1))
        for i in range(0, plat + 1):
            clone_dict(PLATFORMS[i], result)
    else:
        print "  Platform doesn't found!!"
        ret = False
    return ret
    
    
def get_capabilities(data):
    def clean_false_capabilities(ret):
        for k in ret.keys():
            if ret[k] == "false":
                del ret[k]
                
    """ returns a map of capabilities and values """
    ret = {};
    extract_capabilities_by_expressions(data, ret, EXPRESSIONS, True)
    extract_capabilities_by_platform(data, ret)
    clean_false_capabilities(ret)
    extract_capabilities_by_expressions(data, ret, ALTERNATIVE_EXPRESSIONS, False)
    ret['battlewizard_engine'] = 'midp20.std'
    ret['j2me_heap_size'] = '-2'
    ret['j2me_max_jar_size'] = '-2'
        
    return ret
    

def load_device(model_tuple):
    global current_device
    global max_devices
    
    """ returns a map of capabilities and values """
    model_id = model_tuple[0]
    model_name = model_tuple[1]
    
    print "(%s/%s) Downloading %s..." % (current_device, max_devices, model_name)
    current_device += 1
    data = urllib.urlopen("http://developer.sonyericsson.com/device/loadDevice.do?id=" + model_id).read()

    ret = get_capabilities(data)
    ret["battlewizard_engine"] = "midp20.std"

    return (model_tuple, ret)

       

def normalize(tuple):
    def normalize_capability_size(value):
        if value == 'false':
            value = '-1'
        elif value.endswith('KB'):
            value = int(value.split(' KB')[0]) * 1024
        elif value.endswith('MB'):
            value = int(value.split(' MB')[0]) * 1024 * 1024
            
        return value
    
    # normalize size
    caps = tuple[1]
    for cap in caps:
        if cap in ('j2me_max_jar_size', 'j2me_heap_size'):
            caps[cap] = normalize_capability_size(caps[cap])

            

    
def get_devices_list():
#    return [('b7814878-3a02-41a8-8241-1863faa1abd2', 'G700')]
#    return [('4253f545-29a5-4a1d-9190-cd0013abbe30', 'K600i')]
#    return [('3220', 'Nokia 3220')]
#   return [('N97', 'Nokia N97')]

    data = urllib.urlopen("http://developer.sonyericsson.com/device/searchDevice.do?restart=true").read()
    expr = '<option value="">select a phone</option>'
    pattern = re.compile(expr)
    match = pattern.search(data)
    
    #<option value="8f5eeda6-02c8-46d8-ad04-0d9a1e8e6e58">Aino </option>
    #expr = '<option value="[0-9af]{8}-[0-9af]{4}-[0-9af]{4}-[0-9af]{4}-[0-9af]{12}">([0-9a-zA-Z-]*) </option>'
    expr = '<option value="([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})">(\w*)\s+</option>'
    pattern = re.compile(expr)
    ret = []
    while match != None:
        match = pattern.search(data, match.end())
        if match != None:
            ret.append(match.groups())

    return ret

""" Generate new devices depending on the name and the grouping made by manufacturer. 
For example:
    - "Z750" becomes tree devices: "Z750i", "Z750c" and "Z750a"
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
        add_suffix = len(model_name) in (4,5) and model_name[0].isalpha() and model_name[1].isdigit()
        if add_suffix:
            current_suffix = model_name[-1]
            if current_suffix.isdigit() or not model_name[-2].isdigit():
                current_suffix = ''
            for letter in ('i', 'a', 'c'):
                if letter != current_suffix or current_suffix == '':
                    if current_suffix == '':
                        model_name = dev[1] + letter
                    else:
                        model_name = dev[1].rstrip(current_suffix) + letter
                    if not exists_device(devices, model_name) and not exists_device(result, model_name):
                        partial_res.append((dev[0], model_name))

        # add only existing
        exists = False
        for new_dev in partial_res:
            model = new_dev[1]
            if w.exists_device("SonyEricsson", model):
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
    w.set_default_parent('sonyericsson_generic')
    
#    tuples = get_devices(w)
#    print "\nSetting devices..."
#    for d in tuples:
#        model_id = d[0][0]
#        model_name = d[0][1]
#        capabilities = d[1]
#        capabilities["brand_name"] = 'SonyEricsson'
#        capabilities["model_name"] = model_name
#        capabilities["j2me_data_source"] = "sonyericsson_spider"
#        w.set_device(capabilities, None)
        
    # complete with getjar
    spider = SonyEricssonGetJarSpider(w)
    spider.dump()

    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_spider.xml')
    print "\nFinished!"
        