import subprocess
import ConfigParser
import sys

settings_path = "/var/www/lab_app/camera-settings.ini"
HorisontalFlip = "-hf"
VerticalFlip = "-vf"
x0 = 0.2
y0 = 0.3
dX = 0.5
dY = 0.5
pW = 360
pH = 360
sharpness =  -100
contrast = 100
brightness = 40
saturation = -40
awb = 'cloud'
ex = 'beach'
  
def get_photo(w, h, img_name):
  readSettings()
  cmd = "raspistill -w " + str(w) + " -h " + str(h) 
  cmd += " -a 12 -t 100 " + HorisontalFlip + " -o " + img_name
  subprocess.call(cmd, shell=True)
  return [x0, y0, dX, dY, pW, pH, sharpness, 
          contrast, brightness, saturation, awb, ex]
 
def get_photo_area(img_name):
  readSettings()
  cmd = "raspistill -w " + str(pW) + " -h " + str(pH)  
  #a 12 = show the date and time
  cmd += " -a 12 -t 100 " + HorisontalFlip 
  cmd += " -br " + str(brightness)
  cmd += " -co " + str(contrast)
  cmd += " -sh " + str(sharpness)
  cmd += " -sa " + str(saturation)
  cmd += " -awb " + awb
  cmd += " -ex " + ex
  cmd += " -roi " + str(x0) + ',' + str(y0) + ',' + str(dX) + ',' + str(dY)
  cmd += " -o " + img_name
  print cmd
  subprocess.call(cmd, shell=True)  
  return [x0, y0, dX, dY, pW, pH, sharpness, 
          contrast, brightness, saturation, awb, ex]
  
def readSettings(): 
  Config = ConfigParser.SafeConfigParser()
  Config.read(settings_path)
  global x0, y0, dX, dY, pW, pH, awb, ex
  global sharpness, contrast, brightness, saturation  
  x0 = Config.getfloat("Camera", "leftConerX")
  y0 = Config.getfloat("Camera", "leftConerY")
  dX = Config.getfloat("Camera", "width")
  dY = Config.getfloat("Camera", "height")
  pW = Config.getint("Camera", "img_size_width")
  pH = Config.getint("Camera", "img_size_height")
  awb = Config.get("Camera", "awb")
  ex = Config.get("Camera", "exposure")
  sharpness = Config.getint("Camera", "sharpness")
  contrast = Config.getint("Camera", "contrast")
  brightness = Config.getint("Camera", "brightness")
  saturation = Config.getint("Camera", "saturation")  
  print [x0, y0, dX, dY, pW, pH, sharpness, 
          contrast, brightness, saturation, awb, ex]
  
def saveSettings(x0, y0, dX, dY, sh, co, br, sa, awb, ex):   
  parser = ConfigParser.SafeConfigParser()
  parser.add_section('Camera')
  parser.set('Camera', 'leftConerX', x0)
  parser.set('Camera', 'leftConerY', y0)
  parser.set('Camera', 'width', dX)
  parser.set('Camera', 'height', dY)
  parser.set('Camera', 'img_size_width', str(pW))
  parser.set('Camera', 'img_size_height', str(pH))
  parser.set('Camera', 'sharpness', sh)
  parser.set('Camera', 'contrast', co)
  parser.set('Camera', 'brightness', br)
  parser.set('Camera', 'saturation', sa)
  parser.set('Camera', 'awb', awb)
  parser.set('Camera', 'exposure', ex) 
  with open(settings_path, 'wb') as configfile:
    parser.write(configfile)
    
    
def loadDefault():
  parser = ConfigParser.SafeConfigParser()
  parser.add_section('Camera')
  parser.set('Camera', 'leftConerX', '0.2')
  parser.set('Camera', 'leftConerY', '0.3')
  parser.set('Camera', 'width', '0.5')
  parser.set('Camera', 'height', '0.5')
  parser.set('Camera', 'img_size_width', '360')
  parser.set('Camera', 'img_size_height', '360')
  parser.set('Camera', 'sharpness', '-100')
  parser.set('Camera', 'contrast', '+100')
  parser.set('Camera', 'brightness', '40')
  parser.set('Camera', 'saturation', '-40')
  parser.set('Camera', 'awb', 'cloud')
  parser.set('Camera', 'exposure', 'beach') 
  with open(settings_path, 'wb') as configfile:
    parser.write(configfile)    
    