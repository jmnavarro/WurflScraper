import re
import urllib
from wurlf import *


class GetJarSpider:
    EXPRESSIONS = {
        'j2me_screen_width'          : re.compile('Resolution</font></b>:&nbsp;&nbsp;(\d*)w\s*[Xx]\s*\d*h</td>'),
        'j2me_screen_height'         : re.compile('Resolution</font></b>:&nbsp;&nbsp;\d*w\s*[Xx]\s*(\d*)h</td>'),
        'j2me_heap_size'             : re.compile('Heap Size \(Bytes\)</font></b>:&nbsp;&nbsp;(\d*)</td>'),
        'j2me_max_jar_size'          : re.compile('Jar Size \(Bytes\)</font></b>:&nbsp;&nbsp;(\d*)</td>'),
        'j2me_max_record_store_size' : re.compile('RMS Store Size \(Bytes\)</font></b>:&nbsp;&nbsp;(\d*)</td>'),
        'j2me_cldc_1_0'              : re.compile('<b>CLDC version</b>:</font>.*1\.0</td>'),  
        'j2me_cldc_1_1'              : re.compile('<b>CLDC version</b>:</font>.*1\.1</td>'),
        'j2me_midp_1_0'              : re.compile('<b>MIDP version</b>:</font>.*1\.0</td>'), 
        'j2me_midp_2_0'              : re.compile('<b>MIDP version</b>:</font>.*2\.0</td>'),
        'j2me_midp_2_1'              : re.compile('<b>MIDP version</b>:</font>.*2\.1</td>'),
        'jsr_66'                     : re.compile('JSR-66'),
        'jsr_75'                     : re.compile('JSR-75'),
        'jsr_82'                     : re.compile('JSR-82'),
        'jsr_120'                    : re.compile('JSR-120'),
        'jsr_135'                    : re.compile('JSR-135'),
        'jsr_169'                    : re.compile('JSR-169'),
        'jsr_172'                    : re.compile('JSR-172'),
        'jsr_177'                    : re.compile('JSR-177'),
        'jsr_179'                    : re.compile('JSR-179'),
        'jsr_180'                    : re.compile('JSR-180'),
        'jsr_184'                    : re.compile('JSR-184'),
        'jsr_185'                    : re.compile('JSR-185'),
        'jsr_195'                    : re.compile('JSR-195'),
        'jsr_205'                    : re.compile('JSR-205'),
        'jsr_209'                    : re.compile('JSR-209'),
        'jsr_211'                    : re.compile('JSR-211'),
        'jsr_216'                    : re.compile('JSR-216'),
        'jsr_217'                    : re.compile('JSR-217'),
        'jsr_219'                    : re.compile('JSR-219'),
        'jsr_226'                    : re.compile('JSR-226'),
        'jsr_229'                    : re.compile('JSR-229'),
        'jsr_234'                    : re.compile('JSR-234'),
        'jsr_238'                    : re.compile('JSR-238'),
        'jsr_239'                    : re.compile('JSR-239'),
        'jsr_248'                    : re.compile('JSR-248'),
        'jsr_256'                    : re.compile('JSR-256'),
        'jsr_927'                    : re.compile('JSR-927')
    }

    
    def __init__(self, brand, wurfl, default_engine):
        self.brand = brand
        self.default_engine = default_engine
        self.wurfl = wurfl
        self.max_devices = 0
        self.current_device = 1

        
    def dump(self):
        tuples = self.get_devices()
        
        print "\nSetting devices..."
        for d in tuples:
            if d[0].__class__ == str:
                model_id = d[0]
                capabilities = d[1]
                self.wurfl.set_device_by_id(model_id, capabilities, "getjar_spider")
            else:
                model_id = d[0][0]
                model_name = d[0][1]
                capabilities = d[1]
                capabilities["brand_name"] = self.normalize_brand_name(self.brand)
                capabilities["model_name"] = model_name
                dev_id = self.normalize_device_id(model_id, model_name) 
                if dev_id:
                    self.wurfl.set_device_by_id(dev_id, capabilities, "getjar_spider")
                else:
                    self.wurfl.set_device(capabilities, "getjar_spider")


    def get_devices(self):
        """ returns a map of devices and capabilities xml"""
        devs = self.get_devices_list()
        self.max_devices = len(devs)
        capabilities_tuples = map(self.load_device, devs)
        map(self.normalize_device_tuple, capabilities_tuples)
        
        return capabilities_tuples

        
    def get_devices_list(self):
        def remove_duplicated(tuples):
            ret = []
            for d in tuples:
                if not d in ret:
                    ret.append(d)
            return ret

        #return [('7130', '7130')]
        
        data = urllib.urlopen("http://devices.getjar.com/device/%s" % self.brand).read()
        expr = re.compile('/device/%s/(.*)[\'"]>%s (.*)</a>' % (self.brand, self.brand))
        match = expr.search(data)
        ret = []	
        while match:
            id = match.group(1)
            model = match.group(2)
            if self.include_device(id, model):
                model = self.normalize_model_name(model)
                ret.append((id, model))
            match = expr.search(data, match.end())
    
        return remove_duplicated(self.normalize_devices_list(ret))


    def normalize_device_tuple(self, tuple):
        caps = tuple[1]
        to_remove = []
        for cap in caps:
            if cap in ('j2me_max_jar_size', 'j2me_heap_size', 'j2me_max_record_store_size', 'j2me_screen_width', 'j2me_screen_height'):
                value = caps[cap]
                if value[0] == '-':
                    value = value[1:len(value)]
                if not value.isdigit():
                    to_remove.append(cap)
        
        for cap in to_remove:
            del caps[cap]


    def include_device(self, model_id, model_name):
        return True
            
    def normalize_devices_list(self, devices):
        return devices
    
    def normalize_model_name(self, model_name):
        return model_name

    def normalize_brand_name(self, brand_name):
        return brand_name

    def normalize_capability_value(self, capability_name, value):
        return value
    
    def normalize_device_id(self, model_id, model_name):
        return None
    
    def get_engine(self, model_id, model_name, capabilities):
        return self.default_engine
    
    def get_expressions(self):
        return self.EXPRESSIONS

    
    def load_device(self, model_tuple):
        """ returns a map of capabilities and values """
        model_id = model_tuple[0]
        model_name = model_tuple[1]

        print "(%s/%s) Downloading %s..." % (self.current_device, self.max_devices, model_name)
        self.current_device += 1
        data = urllib.urlopen("http://devices.getjar.com/device/%s/%s" % (self.brand, model_id)).read()
    
        ret = self.get_capabilities(data, model_name, self.get_expressions())

        if not self.wurfl.patch_overwrites_value(self.normalize_brand_name(self.brand), model_name, "battlewizard_engine"):
            ret["battlewizard_engine"] = self.get_engine(model_id, model_name, ret)
        
        return (model_tuple, ret)


    def get_capabilities(self, data, model_name, expressions):
        """ returns a map of capabilities and values """
        ret = {};
        for key in expressions.keys():
            if not self.wurfl.patch_overwrites_value(self.normalize_brand_name(self.brand), model_name, key):
                match = expressions[key].search(data)
                self.set_capability(key, match, ret)
                
        return ret

    
    def set_capability(self, key, match, ret):
        val = None
        if match:
            if len(match.groups()) >= 1:
                val = self.normalize_capability_value(key, match.group(1))
            else:
                val = self.normalize_capability_value(key, 'true')
        else:
            val = self.normalize_capability_value(key, 'false')

        if val:
            ret[key] = val
            