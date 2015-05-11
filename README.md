# Quake 2 Map to FBX

### NOTE: This is a WIP. The program reads map files and creates the polygons but does not yet export to FBX. That will be coming very soon and I will remove this note.

A simple program for exporting Quake 2 map format files to FBX.
FBX is a data exchange format commonly used by modern game engines and 3D modeling software.
This tool is being created just for fun. If you are a game hacker who wants to mess around with the Vampire maps
in a 3D software, this is the tool for you.

## Features:
- Exports all brushes into polygonal objects
- Exports texture coordinates
- Creates an FBX containing a scene of the map file for viewing in a 3D editing software

## How I made it:
I downloaded the quake 2 tools source code and used the QE4 source code to convert the brush plane data into UV'd polygons.
I used the Autodesk python FBX SDK to create the FBX file.

## What you need:
- A map file created with a QuakeEd4 based map editor (Embrace, QE4, QERadiant, WorldCraft)
- Textures found in the VtMR texture archive or the Quake 2 texture archive
- The FBX SDK and FBX python SDK installed
- Python Pillow Imaging Library 2.8.1 or greater