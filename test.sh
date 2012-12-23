#!/bin/sh
#echo "Le 1er paramètre est : $1"
#blender --background ~/blend/textest2.blend --python background.py
#blender --background blend/smallchar.blend --python background.py
blender --background $1 --python background.py
#cp $1 ${1}.bin

