#!/bin/bash
name=monitoringrc
#echo $name
#rm -f $name.qrc $name.rcc
#echo "Running resource compiler"

#Copy required files to local ./icons folder
python3 buildresources.py

# Create the correct folder tree
cd icons
mkdir icons
mv win11-blue icons

# Run the resource compiler
rcc --project --root icons -o ../$name.qrc
mv ../$name.qrc .
rcc --binary $name.qrc -o ../$name.rcc
#rcc -g python $name.qrc -o $name.py

cd ..

# Move/remove artefacts
#mv icons/$name.qrc ..
rm -rf icons

echo "Please, copy resource file $name.rcc to PROJECT_ROOT/src/gui folder"
