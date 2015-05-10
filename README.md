# Vampire the Masquerade Redemption Map to FBX

### NOTE: This is a WIP. I will remove this line once the program actually works

A simple program for exporting the VtMR map files (Quake 2 map format) to FBX.
FBX is a data exchange format commonly used by modern game engines and 3D modeling software.
This tool is being created just for fun. If you are a game hacker who wants to mess around with the Vampire maps
in a 3D software, this is the tool for you.

This MIGHT also export Quake 2 maps to FBX format. If it doesn't, the amount of work required to do so would be small.

## Features:
- Exports all brushes into polygonal objects
- Exports texture coordinates
- Creates an FBX containing a scene of the map file for viewing in a 3D editing software

## How I made it:
I downloaded the quake 2 tools source code and used the QE4 source code to convert the brush plane data into UV'd polygons.
I used the Autodesk python FBX SDK to create the FBX file.

## What you need:
- A map file created with the embrace map editor
- Textures found in the VtMR game archives
- The FBX SDK and FBX python SDK installed
- PIL (Python Image Library)