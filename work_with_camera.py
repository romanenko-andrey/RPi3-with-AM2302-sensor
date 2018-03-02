import subprocess

def get_photo(w, h, img_name):
  cmd = "raspistill -w " + w + " -h " + h + " -t 100 -vf -hf -o " + img_name
  subprocess.call(cmd, shell=True)