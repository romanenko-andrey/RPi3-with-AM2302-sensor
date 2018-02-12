import ConfigParser
inifilename = "/var/www/lab_app/settings.ini"
Config = ConfigParser.ConfigParser()
Config.read(inifilename)

#READ
#Config.sections()
#Config.getint(section, option)
#Config.getboolean(section, option) 
#Config.getfloat(section, option) 

#WRITE
#Config.add_section('Person')
#Config.set('Person','HasEyes',True)
#Config.set('Person','Age', 50)

#SET_NEW_INI_FILE
#cfgfile = open(new_ini_file_name,'w')
#Config.write(cfgfile)
#cfgfile.close()

#Name = ConfigSectionMap("SectionOne")['name']
def ReadSection(section):
  dict1 = {}
  options = Config.options(section)
  for option in options:
    try:
      dict1[option] = Config.get(section, option)
      if dict1[option] == -1:
        DebugPrint("skip: %s" % option)
    except:
      print("exception on %s!" % option)
      dict1[option] = None
  return dict1