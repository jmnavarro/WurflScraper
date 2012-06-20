import re
import urllib
from wurlf import *
import os
import shutil
from getjar_spider import GetJarSpider


class MotorolaGetJarSpider(GetJarSpider):
    def __init__(self, wurfl):
        GetJarSpider.__init__(self, "Motorola", wurfl, "midp20.std")
        
    def normalize_model_name(self, model_name):
        return model_name.replace("Motorola ", "")



PDF_EXPRESSIONS = {
    'j2me_screen_width'  : [re.compile('Full\-Screen:\s*(\d*)\s*[xX]\s*\d*'), re.compile('(\d*)\s?x\s?\d* \(\d*[kK] colors\)')],
    'j2me_screen_height' : [re.compile('Full\-Screen:\s*\d*\s*[xX]\s*(\d*)'), re.compile('\d*\s?x\s?(\d*) \(\d*[kK] colors\)')],
    #'j2me_heap_size'     : [re.compile('compliant\s*([\d\.]*\s*[MK]B)'), re.compile('Heap Size\s*([\d\.]*\s*[KM][bB])')],
    #'j2me_max_jar_size'  : [re.compile('MIDlet storage ava\w*\s*([\d\.]*\s*[KM][bB])'), re.compile('MIDlet\s*storage\s*ava\w*')],
}

HTML_EXPRESSIONS = {
    'j2me_cldc_1_0'      : [re.compile('<li>.*\(CLDC 1\.0\)</li>')],
    'j2me_cldc_1_1'      : [re.compile('<li>.*\(CLDC 1\.1\)</li>')],
    'j2me_midp_1_0'      : [re.compile('<li>.*\(MIDP 1\.0\)</li>')],
    'j2me_midp_2_0'      : [re.compile('<li>.*\(MIDP 2\.0\)</li>')],
    'j2me_midp_2_1'      : [re.compile('<li>.*\(CLDC 2\.1\)</li>')],
    'jsr_66'             : [re.compile('<li>JSR 66.*</li>')],
    'jsr_75'             : [re.compile('<li>JSR 75.*</li>')],
    'jsr_82'             : [re.compile('<li>JSR 82.*</li>')],
    'jsr_120'            : [re.compile('<li>JSR 120.*</li>')],
    'jsr_135'            : [re.compile('<li>JSR 135.*</li>')],
    'jsr_169'            : [re.compile('<li>JSR 169.*</li>')],
    'jsr_172'            : [re.compile('<li>JSR 172.*</li>')],
    'jsr_177'            : [re.compile('<li>JSR 177.*</li>')],
    'jsr_179'            : [re.compile('<li>JSR 179.*</li>')],
    'jsr_180'            : [re.compile('<li>JSR 180.*</li>')],
    'jsr_184'            : [re.compile('<li>JSR 184.*</li>')],
    'jsr_185'            : [re.compile('<li>JSR 185.*</li>')],
    'jsr_195'            : [re.compile('<li>JSR 195.*</li>')],
    'jsr_205'            : [re.compile('<li>JSR 205.*</li>')],
    'jsr_209'            : [re.compile('<li>JSR 209.*</li>')],
    'jsr_211'            : [re.compile('<li>JSR 211.*</li>')],
    'jsr_216'            : [re.compile('<li>JSR 216.*</li>')],
    'jsr_217'            : [re.compile('<li>JSR 217.*</li>')],
    'jsr_219'            : [re.compile('<li>JSR 219.*</li>')],
    'jsr_226'            : [re.compile('<li>JSR 226.*</li>')],
    'jsr_229'            : [re.compile('<li>JSR 229.*</li>')],
    'jsr_234'            : [re.compile('<li>JSR 234.*</li>')],
    'jsr_238'            : [re.compile('<li>JSR 238.*</li>')],
    'jsr_239'            : [re.compile('<li>JSR 239.*</li>')],
    'jsr_248'            : [re.compile('<li>JSR 248.*</li>')],
    'jsr_256'            : [re.compile('<li>JSR 256.*</li>')],
    'jsr_927'            : [re.compile('<li>JSR 927.*</li>')],
}



max_devices = 0
current_device = 1
tastephone_html = None


def extract_capabilities(data, expressions, ret, start = 0):
    for key in expressions.keys():
        for expr in expressions[key]:
            match = expr.search(data, start)
            if match != None:
                leng = len(match.groups())
                if leng >= 1:
                    ret[key] = match.group(leng)
                else:
                    ret[key] = 'true'
        if not ret.has_key(key):
            ret[key] = 'false'


def download_specs_pdf_sheet(html):

    from pdf2txt import Pdf2Txt

    def get_pdf(name):

        def download(name):
            def is_pdf(filename):
                """ returns true is specified file is a pdf"""
                file = open(filename, mode='rb')
                try:
                    str = file.read(5)
                    ret = (str == '%PDF-')
                finally:
                    file.close()
                return ret
            
            """ downloads the pdf specified from motorola """
            #print "    Downloading specs..."
            pdf = urllib.urlretrieve("http://developer.motorola.com/docstools/specsheets/%s.pdf/" % name)
            pdffile = pdf[0]
            if not is_pdf(pdffile):
                pdffile = None
            return pdffile
    
        def get_from_cache(name):
            filename = "./motorola-pdf-cache/%s.pdf" % name
            if not os.path.exists(filename):
                filename = None
            return filename
        
        def add_to_cache(pdffile, name):
            cached = "./motorola-pdf-cache/%s.pdf" % name
            shutil.copyfile(pdffile, cached)
            return cached
        
        """ get the pdf from local cache (if exists) or from remote """
        filename = get_from_cache(name)
        if not filename:
            filename = add_to_cache(download(name), name)
        return filename
    
    ret = None
    expr = re.compile("<li>\s*<a href='/docstools/specsheets/(\w*).pdf/'><img class='bullet'\s*src='/images/icons/bullet/pdf'\s*alt='\(PDF\)'")
    match = expr.search(html)
    if match != None:
        pdffile = get_pdf(match.group(1))
        if pdffile:
            ret = Pdf2Txt().dump(pdffile)
        else:
            print "    Can't get PDF! Is under login??"
    else:
        print "   Can't find pdf!"

    return ret


def manage_pdf_max_jar_size(specs, ret):
    value = '-2'
    if ret['j2me_max_jar_size'] == 'true':
        expr = re.compile('compliant\s*[\d\.]* [MK]B\s*[\d.\.]* [MK]B\s*([\w ]*)')
        match = expr.search(specs)
        if match != None and len(match.groups()) >= 1:
            str = match.group(1)
            if str == 'Limited only by available memory':
                value = '-1'

    ret['j2me_max_jar_size'] = value
    
    
def get_capabilities_from_tastephone(model_name, caps):
    TASTEPHONE_DEVICE_EXPR = '<a .* href="MIDP_Java_telephone.jsp.*brand=Motorola.*">\s*<span id=".*">%s</span></a>'
    
    TASTEPHONE_EXPRESSIONS = {
        'j2me_screen_width'  : [re.compile('<span id=".*" title="Screen">(\d*)x\d*</span></td>')],
        'j2me_screen_height' : [re.compile('<span id=".*" title="Screen">\d*x(\d*)</span></td>')],
    }
    
    global tastephone_html
    
    if not tastephone_html:
        tastephone_html = urllib.urlopen("http://www.club-java.com/TastePhone/J2ME/MIDP_Benchmark.jsp").read()
        
    expr = re.compile(TASTEPHONE_DEVICE_EXPR % model_name)
    match = expr.search(tastephone_html)
    if not match:
        expr = re.compile(TASTEPHONE_DEVICE_EXPR % model_name.replace(" ", ""))
        match = expr.search(tastephone_html)
        
    if match:
        extract_capabilities(tastephone_html, TASTEPHONE_EXPRESSIONS, caps, match.end())
        print "     From tastephone: %s x %s" % (caps['j2me_screen_width'], caps['j2me_screen_height'])
    
    
def get_capabilities(model_name, data):
    
    def manage_invalid_capabilities(ret):
        keys = ('j2me_screen_width', 'j2me_screen_height', 'j2me_heap_size', 'j2me_max_jar_size')
        for k in keys:
            if ret.has_key(k) and ret[k] == 'false':
                del ret[k]

    def missing_mandatory_capabilities(caps):
        return not caps.has_key('j2me_screen_width') or not caps.has_key('j2me_screen_height')
     
    ret = {}
    extract_capabilities(data, HTML_EXPRESSIONS, ret)
    specs = download_specs_pdf_sheet(data)
    if specs:
        extract_capabilities(specs, PDF_EXPRESSIONS, ret)
        #manage_pdf_max_jar_size(specs, ret)
        
    manage_invalid_capabilities(ret)
    
    if missing_mandatory_capabilities(ret):
        get_capabilities_from_tastephone(model_name, ret)
    return ret
    

def load_device(model_tuple):
    global current_device
    global max_devices
    
    """ returns a map of capabilities and values """
    model_id = model_tuple[0]
    model_name = model_tuple[1]
    
    print "(%s/%s) Downloading %s..." % (current_device, max_devices, model_name)
    current_device += 1
    data = urllib.urlopen("http://developer.motorola.com/products/handsets/" + model_id).read()

    ret = get_capabilities(model_name, data)
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
#    return [('motorazrv3cldc11/', fix_model_name('MOTORAZR V3 (CLDC 1.1)'))]
#    return [('motorokre6/', 'MOTOROKR E6/E6e')]
#    return [('motoq11/', 'MOTO Q11')]
#    return [('motoslvrl7i_l7e/', 'MOTOSLVR L7i/L7e')]
#    return [('motoslvrl7/', 'MOTOSLVR L7')]

    data = urllib.urlopen("http://developer.motorola.com/platforms/java/?num=all").read()
    expr = '<h4>\s*<a href=[\'"]/products/handsets/([\w/]*)[\'"]>(.*)</a>\s*</h4>'
    pattern = re.compile(expr)

    ret = []
    match = pattern.search(data)
    while match != None:
        id = match.group(1)
        model = fix_model_name(match.group(2))
        ret.append((id, model))
        match = pattern.search(data, match.end())

    return ret


""" Generate new devices depending on the name and the grouping made by manufacturer. 
For example:
    - "MOTORAZR V3t" becomes tree devices: "MOTORAZR V3t", "RAZR V3t" and "V3t"
    - "MOTOSLVR L7i/L7e" becomes seven devices: "MOTOSLVR L7i/L7e", "MOTOSLVR L7i", "MOTOSLVR L7e", "SLVR L7i", "SLVR L7e", "L7i" and "L7e"
Once all devices are generated, those not existing in original wurfl.xml are removed 
"""
def duplicate_devices(tuples, w):
    def duplicate_device(dev, w, result):
        partial_res = []
        partial_res.append((dev[0], fix_model_name(dev[1])))
        if not duplicate_device_for_slash(dev, partial_res):
            duplicate_device_for_name(dev, partial_res)

        # add only existing
        exists = False
        for new_dev in partial_res:
            model = new_dev[1]
            if w.exists_device("Motorola", model):
                result.append(new_dev)
                exists = True

                
        if not exists:
            # add all
            for new_dev in partial_res:
                result.append(new_dev)

    def duplicate_device_for_slash(dev, result):
        name = dev[1]
        ret = name.find('/') > -1
        if ret:
            parts = name.split(' ')
            if len(parts) == 1:
                common = ""
                parts = parts[0].split('/')
            else:
                common = parts[0].strip()
                parts = parts[1].split('/')
            # first
            new_model = "%s %s" % (common, parts[0].strip())
            new_model = fix_model_name(new_model)
            new_dev = (dev[0], new_model)
            result.append(new_dev)
            duplicate_device_for_name(new_dev, result)
            # second
            new_model = "%s %s" % (common, parts[1].strip())
            new_model = fix_model_name(new_model)
            new_dev = (dev[0], new_model)
            result.append(new_dev)
            duplicate_device_for_name(new_dev, result)
        return ret
            
    def duplicate_device_for_name(dev, result):
        name = dev[1]
        if name.find('MOTO') > -1:
            new_name = name.replace("MOTO", "").strip()
            result.append((dev[0], fix_model_name(new_name)))
            
        parts = name.split(" ")
        if len(parts) > 1:
            parts[0] = ""
            new_name = " ".join(parts)
            result.append((dev[0], fix_model_name(new_name.strip())))
            
    ret = []
    for d in tuples:
        duplicate_device(d, w, ret)
            
    return ret

            
def fix_model_name(model):
    model = model.replace('Q 11', 'Q11')            # fix Q 11 -> Q11
    model = model.replace("(CLDC 1.0)","CLDC1.0")   # V3
    model = model.replace("(CLDC 1.1)","CLDC1.1")   # V3
    return model


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
    
    urllib.urlcleanup() # cleanup

    return capabilities_tuples


if __name__ == '__main__':
    w = Wurfl('../wurfl.xml', '../wurfl_patch.xml')
    w.set_default_parent('mot_mib20_generic')

#    tuples = get_devices(w)
#    print "\nSetting devices..."
#    for d in tuples:
#        model_id = d[0][0]
#        model_name = d[0][1]
#        capabilities = d[1]
#        capabilities["brand_name"] = 'Motorola'
#        capabilities["model_name"] = model_name
#        capabilities["j2me_data_source"] = "motorola_spider"
#        w.set_device(capabilities, None)
        
    # complete with getjar
    mot = MotorolaGetJarSpider(w)
    mot.dump()

    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_spider.xml')
    print "\nFinished!"
        
        
        
