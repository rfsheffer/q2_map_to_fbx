# Quake 2 Map to FBX

A simple program for exporting Quake 2 map format files to FBX.
FBX is a data exchange format commonly used by modern game engines and 3D modeling software.
This tool is being created just for fun. If you are a game hacker who wants to mess around with the Vampire maps
in a 3D software, this is the tool for you.

Here is an example exported from the tool. It is the Prague North Quarter from Vampire the Masquerade : Redemption :
![alt tag](http://s22.postimg.org/y464wfy01/north_district_night.jpg)

## Features:
- Exports all brushes into polygonal objects
- Exports texture coordinates
- Creates an FBX containing a scene of the map file for viewing in a 3D editing software

## Future Features:
- Remove all faces which are not visible from within the hull of the map

## How I made it:
I downloaded the quake 2 QE4 source code and used it as a reference for properly exporting the mesh data from the Quake 2 map files.
I used the Autodesk python FBX SDK to create the FBX file.

## What you need:
- A map file created with a QuakeEd4 based map editor (Embrace, QE4, QERadiant, WorldCraft)
- Textures found in the VtMR texture archive or the Quake 2 texture archive
- The FBX SDK and FBX python SDK installed
- Python Pillow Imaging Library 2.8.1 or greater