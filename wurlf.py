import xml.dom.minidom
import logging
import copy

class Wurfl:
    def attr2map(self, node):
        """ return attribute dictionary """
        theZip = zip(node.attributes.keys(), (x.value for x in node.attributes.values()));
        return dict(theZip);


    def get_capabilities_by_group(self, node, groups):
        """ return a dict with name as keys and value tag as value"""
        capabilities_by_group = {}
        for group in groups:
            d = {}
            group_info = [x for x in node.getElementsByTagName("group") if x.attributes.values()[0].value == group];
            if(group_info):
                group_info = group_info[0];
                for c in group_info.getElementsByTagName("capability"):
                    d[c.attributes.values()[0].value] = c.attributes.values()[1].value;
            capabilities_by_group[group] = d;
        return capabilities_by_group;


    def gen_wurfl(self, filename, source):
        f = open(filename);
        dom = xml.dom.minidom.parse(f)
        f.close()
        print " Wurfl cargado"
        devices = dom.getElementsByTagName("device")
        dom = None
        for d in devices:
            attributes = {}
            attributes["attributes"] = self.attr2map(d)
            id = attributes["attributes"]["id"].lower()
            if source == 'patch':
                if id.find("_ver") < 0 and id.find("_sub") < 0:
                    if not self.groups_by_id.has_key(id):
                        print " WARNING!! Invalid id (%s)???" % id
            
            groups = self.get_capabilities_by_group(d, ["product_info", "j2me", "display"])
            if groups:
                self.normalize(groups)
                if not self.groups_by_id.has_key(id):
                    self.groups_by_id[id] = groups
                else:
                    origen_groups = self.groups_by_id[id]
                    self.update_groups(groups, origen_groups)
                self.groups_by_id[id].update(attributes)
                
            cloned_g = copy.deepcopy(groups)
            if source == 'patch':
                self.patch_data[id] = cloned_g
            elif source == 'wurfl': 
                self.wurfl_data[id] = cloned_g
            elif source == 'migrate':
                self.migrate_data[id] = cloned_g
            
        devices = None
        return
        

    def migrate_wurfl(self, new_wurfl):

        def get_or_build_migrated_device_id(old_id, brand, model):
            if self.exists_device(brand, model):
                c = 0
                size = len(self.brands[brand][model])
                dev_id = self.brands[brand][model][c]
                exists = self.migrate_data.has_key(dev_id)
                if not exists:
                    exists = self.patch_data.has_key(dev_id)
                c += 1
                while not exists and c < size:
                    dev_id = self.brands[brand][model][c]
                    exists = self.migrate_data.has_key(dev_id)
                    if not exists:
                        exists = self.patch_data.has_key(dev_id)
                    c += 1
                if not exists:
                    dev_id = "generic_%s" % (old_id)
                    exists = self.migrate_data.has_key(dev_id)
                    if not exists:
                        exists = self.patch_data.has_key(dev_id)

                    if not exists:
                        dev_id = None
                        print "ERROR in get_or_build_migrated_device_id!!! old_id=%s brand=%s model=%s" % (old_id, brand, model)
                        for xx in self.brands[brand][model]:
                            print "   Devices: %s" % (xx)

            else:
                dev_id = self.build_device_id(brand, model)

            return dev_id;
        
        def migrate_dev(current, total, dev_id, to_add, parent_id):
            if self.migrate_data.has_key(dev_id):
                # exists same id: user agent and fall_back will be copied in write_patch
                print "+ [%s/%s] Exists %s" % (current, total, dev_id)
            else:
                print "- [%s/%s] DOESNT Exist %s" % (current, total, dev_id)

                # this id doesn't exist in original wurfl: look for new id
                caps = self.getCapabilitiesById(dev_id)
                brand = caps["product_info"]["brand_name"].lower()
                model = caps["product_info"]["model_name"].lower()
                    
                if brand == '' or model == '':
                    print "    - Without brand or model"

                    xxx = caps["attributes"]["user_agent"];
                    new_dev_id = self.get_device_id_by_ua(xxx, dev_id)

                    caps = self.getCapabilitiesById(new_dev_id)
                    
                    if brand == '':
                        brand = caps["product_info"]["brand_name"].lower()
                    if model == '':
                        model = caps["product_info"]["model_name"].lower()
                else:
                    print "    - Getting new id"
                    new_dev_id = get_or_build_migrated_device_id(dev_id, brand, model)

                # el id del padre ha cambiado
                changed_parent = False
                if dev_id == new_dev_id:
                    print "    - New ID is the same %s" % (dev_id)
                    if parent_id != None:
                        attrs = self.groups_by_id[dev_id]["attributes"]
                        if attrs["fall_back"] != parent_id:
                            print "    - Parent changed! old=%s new=%s" % (attrs["fall_back"], parent_id)
                            changed_parent = True


                if dev_id != new_dev_id or changed_parent:
                    if dev_id != new_dev_id:
                        print "    - New ID is different old=%s new=%s" % (dev_id, new_dev_id)

                    if self.patch_data.has_key(dev_id):
                        pinfo = self.patch_data[dev_id]["product_info"]
                        j2me = self.patch_data[dev_id]["j2me"]
                    else:
                        pinfo = self.wurfl_data[dev_id]["product_info"]
                        j2me = self.wurfl_data[dev_id]["j2me"]

                    groups = {'attributes'  : {},
                              'product_info': pinfo,
                              'j2me'        : j2me}

                    if self.groups_by_id.has_key(new_dev_id):
                        self.update_groups(self.groups_by_id[new_dev_id]["attributes"], groups["attributes"])
                        if changed_parent:
                            print "    - Exists in original wurfl Using: UA=%s FB=%s" % (groups["attributes"]["user_agent"], parent_id)
                        else:
                            print "    - Exists in original wurfl Using: UA=%s FB=%s" % (groups["attributes"]["user_agent"], groups["attributes"]["fall_back"])
                    else:
                        fb = self.look_for_parent(brand, model)
                        ua = self.get_user_agent(brand, model)
                        print "    - DOESNT Exist in original wurfl Generated: UA=%s FB=%s" % (ua, fb)
                        
                        groups["attributes"]['id'] = new_dev_id
                        groups["attributes"]['actual_device_root'] = 'true'
                        groups["attributes"]['fall_back'] = fb
                        groups["attributes"]['user_agent'] = ua

                    if changed_parent:
                        groups["attributes"]['fall_back'] = parent_id
                    
                    self.normalize(groups)
                    self.groups_by_id[new_dev_id] = groups
            
                    # add/remove to brands
                    if not self.brands[brand].has_key(model):
                        self.brands[brand][model] = []
                    self.brands[brand][model].append(new_dev_id)
                    if dev_id in self.brands[brand][model]:
                        self.brands[brand][model].remove(dev_id)
                    # add to patch
                    to_add.append((dev_id, new_dev_id, copy.deepcopy(groups)))
                    dev_id = new_dev_id
                else:
                    print "    - New ID is the same %s" % (dev_id)
                    
            return dev_id

        def get_dev_renamed(dev_id, list):
            for e in list:
                if e[0] == dev_id:
                    return e[1]
            return None

            
        print ("Inicializando new wurfl")
        self.migrate_data = {}
        self.gen_wurfl(new_wurfl, 'migrate')
        self.build_brands()
            
        to_add = []
        migrated = []
        total = len(self.patch_data)
        current = 1
        print ("Recorriendo ids del parche...")
        for dev_id in self.patch_data:
            parents = []
            self.get_parents(dev_id, parents)
            parents.reverse()
            parent_id = None
            for p in parents:
                new_id = get_dev_renamed(p, to_add)
                if new_id == None or new_id != p:
                    if new_id != None and new_id != p:
                        p = new_id
                    if p not in migrated:
                        p = migrate_dev(current, total, p, to_add, parent_id)
                        current += 1
                        if p:
                            migrated.append(p)
                parent_id = p

        print "Recorriendo ids para aniadir..."
        total = len(to_add)
        current = 1
        for dev in to_add:
            old_dev_id = dev[0]
            new_dev_id = dev[1]
            g = dev[2]

            print "[%s/%s]  - Old id=%s New id=%s" % (current, total, old_dev_id, new_dev_id)

            if self.patch_data.has_key(old_dev_id):
                del self.patch_data[old_dev_id]
            self.patch_data[new_dev_id] = g

            
    def get_parents(self, dev_id, result):
        result.append(dev_id);
        if dev_id != 'generic' and self.groups_by_id.has_key(dev_id):
            self.get_parents(self.groups_by_id[dev_id]["attributes"]["fall_back"], result)

            
    def get_device_id_by_ua(self, ua, avoid_dev_id):
        for dev_id in self.groups_by_id:
            g = self.groups_by_id[dev_id]
            if dev_id != avoid_dev_id and g["attributes"]["user_agent"] == ua:
                return dev_id
        return None


    def update_groups(self, origen_groups, destino_groups):
        for g in origen_groups:
            if destino_groups.has_key(g):
                destino_groups[g].update(copy.deepcopy(origen_groups[g]))
            else:
                destino_groups[g] = copy.deepcopy(origen_groups[g])
                

    def get_fall_back(self, id):
        if self.groups_by_id.has_key(id):
            return self.builtHeritage(id);
        return None
    
    def getCapabilitiesById(self, id):
        if self.groups_by_id.has_key(id):
            return self.builtHeritage(id);
        return None


    def builtHeritage(self, id):
        """ This method must be only used by the getCapabilities method """
        capabilities = {}
        assert (self.groups_by_id.has_key(id))
        device_group = self.groups_by_id[id]
        #inmutable_device_groups = zip(device_groups.keys(), device_groups.values())
        """ get the all capabilities """
        heritage_groups = self.getHeritage(device_group["attributes"]["fall_back"], capabilities);
        self.update_groups(device_group, capabilities)
        return capabilities;



    def getHeritage(self, id, origen):
        """ This method must be only used by the builtHeritage method """
        if self.groups_by_id.has_key(id):
            groups = self.groups_by_id[id]
            if id.find("root") == - 1:
                #print id
                """ Get capabilities' father """
                self.getHeritage(groups["attributes"]["fall_back"], origen)
                """ insert capabilities """
                #origen.update(c);
                self.update_groups(groups, origen)
                
                
                
    def set_device_by_id(self, dev_id, capabilities, spider):
        if self.groups_by_id.has_key(dev_id):
            g = self.groups_by_id[dev_id]
            self.copy_capabilities_to_groups(capabilities, g)
            self.normalize(g)
#            self.remove_inherited(g)
            # add to patch
            if spider and not g["j2me"].has_key("j2me_data_source"):
                g["j2me"]["j2me_data_source"] = spider
            self.patch_data[dev_id] = copy.deepcopy(g)
        
        
    def set_device(self, capabilities, spider):
        brand_name = capabilities["brand_name"] 
        model_name = capabilities["model_name"]
        print "Setting %s %s" % (brand_name, model_name)
        brand = brand_name.lower()
        model = model_name.lower()
        # look for device as brand and model
        if self.exists_device(brand, model):
            for dev in self.brands[brand][model]:
                g = self.groups_by_id[dev]
                self.copy_capabilities_to_groups(capabilities, g)
                self.normalize(g)
                if spider and not g["j2me"].has_key("j2me_data_source"):
                    g["j2me"]["j2me_data_source"] = spider
#                self.remove_inherited(g)
                # add to patch
                self.patch_data[dev] = copy.deepcopy(g)
        else:
            if spider:
                capabilities["j2me_data_source"] = spider
            self.insert_device(capabilities)


    def exists_device(self, brand, model):
        brand = brand.lower()
        model = model.lower()
        return self.brands.has_key(brand) and self.brands[brand].has_key(model)


    def patch_overwrites_value(self, brand, model, capability):
        brand = brand.lower()
        model = model.lower()
        # es posible que un modelo tenga dos versiones y que una version sobrescriba el valor pero la otra no. que se hace en este caso?
        dev_id = self.get_or_build_device_id(brand, model); 
        return self.patch_overwrites_value_by_id(dev_id, self.get_group(capability), capability)


    def patch_overwrites_value_by_id(self, dev_id, group_name, capability):
        ret = self.patch_data.has_key(dev_id) and self.patch_data[dev_id][group_name].has_key(capability)
        if not ret and self.groups_by_id.has_key(dev_id):
            parent_id = self.groups_by_id[dev_id]["attributes"]["fall_back"]
            if parent_id != 'generic':
                ret = self.patch_overwrites_value_by_id(parent_id, group_name, capability)
        return ret        
    
    
    def get_group(self, cap):
        if cap.startswith("j2me_") or cap.startswith("jsr_") or cap.startswith("battle"):
            return "j2me"
        else:
            return "product_info"
        
        
    def copy_capabilities_to_groups(self, capabilities, groups):
        for c in capabilities:
            g = self.get_group(c)
            groups[g][c] = capabilities[c]


    def get_or_build_device_id(self, brand, model):
        ret = self.get_device_id(brand, model)
        if not ret:
            ret = self.build_device_id(brand, model)

        return ret
    

    def get_device_id(self, brand, model):
        if self.exists_device(brand, model):
            # es posible que exista mas de una version para un modelo concreto porque retornar la primera??    
            dev_id = self.brands[brand][model][0]
        else:
            dev_id = None
            
        return dev_id
    
     
    def build_device_id(self, brand_name, model_name):
        if brand_name == 'rim':
            id = model_name.replace(" ", "") + '_ver1'
        elif brand_name == 'motorola':
            id = 'mot_' + model_name.replace(" ", "_").replace("-", "_") + '_ver1'
        else:
            id = (brand_name + '_' + model_name + '_ver1').replace(' ', '_').replace('-', '_')

        return id
    

    def get_user_agent(self, brand_name, model_name):
        brand = brand_name.lower()
        if brand == 'rim':
            ret = model_name.replace(" ", "")
        elif brand == 'motorola':
            ret = "MOT-" + model_name
        elif brand == 'siemens':
            ret = "SIE-" + model_name
        else:
            ret = brand_name + model_name
        return ret


    def insert_device(self, capabilities):
        # build id
        brand_name = capabilities["brand_name"] 
        model_name = capabilities["model_name"]
        
        print "     Inserting %s %s" % (brand_name, model_name)
        
        brand = brand_name.lower()
        model = model_name.lower()
        
        id = self.build_device_id(brand, model)
        
        #add to groups
        groups = {'attributes' : {}, 'product_info': {}, 'j2me' : {}}
        self.copy_capabilities_to_groups(capabilities, groups)
        
        if self.groups_by_id.has_key(id):
            self.update_groups(self.groups_by_id[id]["attributes"], groups["attributes"])
        else:
            groups["attributes"]['id'] = id
            groups["attributes"]['actual_device_root'] = 'true'
            groups["attributes"]['fall_back'] = self.look_for_parent(brand, model)
            groups["attributes"]['user_agent'] = self.get_user_agent(brand_name, model_name)  
        
        
        self.normalize(groups)
#        self.remove_inherited(groups)
        
        self.groups_by_id[id] = groups

        # add to brands
        if not self.brands[brand].has_key(model):
            self.brands[brand][model] = []
        self.brands[brand][model].append(id)
        
        # add to patch
        self.patch_data[id] = copy.deepcopy(groups)

        
    def normalize(self, groups):
        # normalize midp
        if groups["j2me"].has_key("j2me_midp_2_1") and groups["j2me"]["j2me_midp_2_1"] == "true":
             groups["j2me"]["j2me_midp_2_0"] = "true"
        if groups["j2me"].has_key("j2me_midp_2_0") and groups["j2me"]["j2me_midp_2_0"] == "true":
            groups["j2me"]["j2me_midp_1_0"] = "true"
        # normalize cldc
        if groups["j2me"].has_key("j2me_cldc_1_1") and groups["j2me"]["j2me_cldc_1_1"] == "true":
            groups["j2me"]["j2me_cldc_1_0"] = "true"
        # normalize id
        if groups["product_info"].has_key("id"):
            del groups["product_info"]["id"]
        # normalize screen size
        if groups.has_key("display"): 
            if groups["display"].has_key("resolution_width") and groups["j2me"].has_key("j2me_screen_width"):
                groups["display"]["resolution_width"] = groups["j2me"]["j2me_screen_width"]             
            if groups["display"].has_key("resolution_height") and groups["j2me"].has_key("j2me_screen_height"):
                groups["display"]["resolution_height"] = groups["j2me"]["j2me_screen_height"]
        else:
            groups["display"] = {}
            if groups["j2me"].has_key("j2me_screen_width"):
                groups["display"]["resolution_width"] = groups["j2me"]["j2me_screen_width"]
            if groups["j2me"].has_key("j2me_screen_height"):
                groups["display"]["resolution_height"] = groups["j2me"]["j2me_screen_height"]
        
        
#    def remove_inherited(self, groups):
#        cloned_groups = copy.deepcopy(groups)
#        parent = cloned_groups["attributes"]['fall_back']
#        parent_caps = self.getCapabilitiesById(parent)
#        for g in cloned_groups:
#            if g != "attributes":
#                for cap in cloned_groups[g]:
#                    if parent_caps[g].has_key(cap):
#                        if parent_caps[g][cap] == cloned_groups[g][cap]:
#                            del groups[g][cap]
            
        
    def look_for_parent(self, brand, model):
        devices = self.brands[brand]
        for d in devices.keys():
            if model.startswith(d):
                #look for smallest id for this brand,model
                return self.insensitive_sort(devices[d])[0]
        return self.default_parent;

    
    def insensitive_sort(self, list):
        tupleList = [(x.lower(), x) for x in list]
        tupleList.sort()
        return [x[1] for x in tupleList]

        
    def build_brands(self):
        self.brands = {}
        i = 1
        l = len(self.groups_by_id)
        for id in self.groups_by_id:
            print "(%s/%s) Building brands for %s..." % (i, l, id)
            i += 1
            capabitilies = self.getCapabilitiesById(id)
            if capabitilies["product_info"].has_key("brand_name"):
                brand = capabitilies["product_info"]["brand_name"].lower()
            else: 
                brand = "" 
            if capabitilies["product_info"].has_key("model_name"):
                model = capabitilies["product_info"]["model_name"].lower()
            else:
                model = ""
            if brand <> "" and model <> "":
                if not self.brands.has_key(brand):
                    self.brands[brand] = {}
                if not self.brands[brand].has_key(model):
                    self.brands[brand][model] = []
                self.brands[brand][model].append(id)

        
    def write_patch(self, filename):

        def contains_capability(dev_id, capability, value):
            ret = False
            if self.groups_by_id.has_key(dev_id):
                groups = self.groups_by_id[dev_id]
                group_name = self.get_group(capability)
                if groups[group_name].has_key(capability):
                    ret = (groups[group_name][capability] == value)
                else:
                    ret = False
                if not ret and dev_id != 'generic':
                    ret = contains_capability(groups["attributes"]["fall_back"], capability, value)
            return ret
    
    
        def group_has_caps(id, parent_id, group):
            if id == 'generic':
                return len(group) > 0
            else:
                for cap in group:
                    if not contains_capability(parent_id, cap, group[cap]):
                        return True
            return False
    
            
        def dev_has_caps(id, parent_id, dev_groups):
            for g in dev_groups.iterkeys():
                if g != "attributes" and group_has_caps(id, parent_id, dev_groups[g]):
                    return True
            return False


        def sorted_dict(dict):
            list = []
            for id in dict.iterkeys():
                list.append(id)
            list.sort()
            return list

        
        def escape(str):
            if str:
                str = str.replace("&amp;", "<!<AMP>!>").replace("&", "&amp;").replace("<!<AMP>!>", "&amp;")
            return str

        
        def manage_engine(id, groups):
            full_groups = self.getCapabilitiesById(id)
            if full_groups.has_key("j2me") and full_groups["j2me"].has_key("battlewizard_engine"):
                is_cldc_10 = full_groups["j2me"].has_key("j2me_cldc_1_0") and full_groups["j2me"]["j2me_cldc_1_0"] == 'true' 
                is_cldc_11 = full_groups["j2me"].has_key("j2me_cldc_1_1") and full_groups["j2me"]["j2me_cldc_1_1"] == 'true' 
                is_midp_20 = full_groups["j2me"].has_key("j2me_midp_2_0") and full_groups["j2me"]["j2me_midp_2_0"] == 'true' 
                is_midp_21 = full_groups["j2me"].has_key("j2me_midp_2_1") and full_groups["j2me"]["j2me_midp_2_1"] == 'true'
                is_automatic = full_groups["j2me"].has_key("j2me_data_source") and full_groups["j2me"]["j2me_data_source"] != ''
                if is_automatic and ((not is_cldc_10 and not is_cldc_11) or (not is_midp_20 and not is_midp_21)):
                    if not groups.has_key("j2me"):
                        groups["j2me"] = {}
                    groups["j2me"]["battlewizard_engine"] = ""

                    
        def remove_usefullness_capabilities(group, caps):
            TO_REMOVE = {"product_info" : ("brand_name", "model_name"),
                         "display" : ("resolution_width", "resolution_height")}
            remove_list = []
            for cap in caps:
                if cap not in TO_REMOVE[group]:
                    remove_list.append(cap)
                    
            for cap in remove_list:
                del caps[cap]

                    
        file = open(filename, 'w')
        try:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n<wurfl_patch>\n<version>\n\t<ver>Unkasoft WURFL patch v_x.y.z</ver>\n\t<last_updated>Nov 24, 2008</last_updated>\n\t<official_url>http://www.unkasoft.com/</official_url>\n</version>\n\n<devices>\n')
            
            current = 1
            max = len(self.patch_data)
            for id in sorted_dict(self.patch_data):
                print "(%s/%s) Write %s..." % (current, max, id)
                current += 1
                dev_groups = self.patch_data[id]
                groups = self.groups_by_id[id]
                self.normalize(dev_groups)
                self.normalize(groups)
                remove_usefullness_capabilities("product_info", dev_groups["product_info"])
                remove_usefullness_capabilities("display", dev_groups["display"])
                manage_engine(id, dev_groups)
                attr = groups["attributes"]
                parent_id = attr["fall_back"].lower()
                if dev_has_caps(id, parent_id, dev_groups):
                    attr["id"] = attr["id"].lower()
                    attr["fall_back"] = parent_id
                    attr["user_agent"] = escape(attr["user_agent"])
                    if attr.has_key("actual_device_root"):
                        file.write('\n<device id="%(id)s" user_agent="%(user_agent)s" fall_back="%(fall_back)s" actual_device_root="%(actual_device_root)s">' % attr)
                    else:
                        file.write('\n<device id="%(id)s" user_agent="%(user_agent)s" fall_back="%(fall_back)s">' % attr)
                    for g in sorted_dict(dev_groups):
                        if group_has_caps(id, parent_id, dev_groups[g]) and g != "attributes":
                            file.write('\n\t<group id="%s">' % g)
                            for cap in sorted_dict(dev_groups[g]):
                                if not contains_capability(parent_id, cap, dev_groups[g][cap]) or id == 'generic':
                                    file.write('\n\t\t<capability name="%s" value="%s"/>' % (cap, escape(dev_groups[g][cap])))
                            file.write('\n\t</group>')
                    file.write('\n</device>\n')
            
            file.write('\n</devices>\n\n</wurfl_patch>')
        finally:
            file.close()


    def __init__(self, f, path, build_brands = True):
        self.default_parent = 'generic'
        self.groups_by_id = {}
        print ("Inicializando wurfl")
        self.wurfl_data = {}
        self.gen_wurfl(f, 'wurfl')
        print ("Inicializando wurfl_patch")
        self.patch_data = {}
        self.gen_wurfl(path, 'patch')
        if build_brands:
            self.build_brands()
        
        
    def set_default_parent(self, parent):
        self.default_parent = parent


    def insert_new_device(wurfl_device):
        print ("El device %s se ha anadido al patch" % wurfl_device["id"])
        devices = dom.getElementsByTagName("devices");
        # devices = dom.getElementsByTagName("device");
        newDevice = dom.createElement("device");
        if wurfl_device.has_key("actual_device_root"):
            newDevice.setAttribute("actual_device_root", wurfl_device["actual_device_root"]); 
        newDevice.setAttribute("fall_back", wurfl_device["fall_back"].lower()); 
        newDevice.setAttribute("id", wurfl_device["id"].lower());
        newDevice.setAttribute("user_agent", wurfl_device["user_agent"]); 
        newGroup = dom.createElement("group");
        newGroup.setAttribute("id", "j2me");
        newDevice.appendChild(newGroup);
        insert_capability(newGroup, "jsr_75");
        devices[0].appendChild(newDevice);
        global addedDevices;
        addedDevices += 1;

