from wurlf import *

if __name__ == '__main__':
    w = Wurfl('../../../wurfl-old-mod.xml', '../../../wurfl_patch-mod.xml', False)
    w.migrate_wurfl('../../../wurfl.xml')
#    w = Wurfl('../../../wurfl-old-min.xml', '../../../wurfl_patch-min.xml', False)
#    w.migrate_wurfl('../../../wurfl-new-min.xml')
    
    print "\nWriting to file..."
    w.write_patch('./wurfl_patch_migrated.xml')
    print "\nFinished!"
        