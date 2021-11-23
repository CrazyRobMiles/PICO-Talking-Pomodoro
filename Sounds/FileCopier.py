# Copies the sound files onto MicroSD card
# Copies in the correct order, making sure that they are added
# in sequence.

# Rob Miles

import os
import shutil
import time

print("Starting")
source = "Sounds/soundfiles"
dest = 'e:/'

# Spin through the files in the directory
for dirName, subdirList, fileList in os.walk(source):
    for fname in fileList:
        sourceName = dirName+'/'+fname
        destName = dest + fname
        print(sourceName,'to',destName)
        shutil.copyfile(sourceName, destName)
        time.sleep(1)

