import optparse
import fbx
import id_map

__author__ = 'Ryan'


def add_entity_to_scene(scene, entity, brush_index):
    """
    Adds a brush as a scene node
    :param scene: The scene to add the brushes to
    :param entity: The entity to take the brushes from
    :param brush_index: The brush index, this should be a unique ID per brush
    :return The number of brushes added
    """

    # Obtain a reference to the scene's root node.
    root_node = scene.GetRootNode()

    for brush in entity.brushes:

        # ignore requested brushes with certain textures applied
        # if brush.faces[0].texture is not None and 'Vienna/DKwall03_5_v' in brush.faces[0].texture.texture_path:
        #    continue

        # Create a new node in the scene.
        new_node = fbx.FbxNode.Create(scene, 'brushNode{0}'.format(brush_index))
        root_node.AddChild(new_node)

        # Create a new mesh node attribute in the scene, and set it as the new node's attribute
        new_mesh = fbx.FbxMesh.Create(scene, 'brushMesh{0}'.format(brush_index))
        new_node.SetNodeAttribute(new_mesh)

        # accumulate all of the brush face points
        brush_points = []
        for face in brush.faces:
            if face.winding is None:
                # Not all faces work out, this is just some quake quirk or something
                continue

            for i in range(0, face.winding.numpoints):
                point = face.winding.points[i]
                brush_points.append(fbx.FbxVector4(point[0], point[1], point[2]))

        # init the control points we are going to set
        new_mesh.InitControlPoints(len(brush_points))

        # set all control points
        for i in range(0, len(brush_points)):
            new_mesh.SetControlPointAt(brush_points[i], i)

        # now join all the points
        cur_poly = 0
        cur_point = 0
        for face in brush.faces:
            if face.winding is None:
                # Not all faces work out, this is just some quake quirk or something
                continue

            new_mesh.BeginPolygon(cur_poly)

            for i in range(0, face.winding.numpoints):
                new_mesh.AddPolygon(cur_point)
                cur_point += 1

            new_mesh.EndPolygon()
            cur_poly += 1

        if cur_point != len(brush_points):
            raise Exception('Number of points plotted on polygons not the number of actual polys!')

        brush_index += 1

    return len(entity.brushes)


def save_scene(filename, fbx_manager, fbx_scene, as_ascii=False):
    """ Save the scene using the Python FBX API """
    exporter = fbx.FbxExporter.Create(fbx_manager, '')

    if as_ascii:
        # DEBUG: Initialize the FbxExporter object to export in ASCII.
        ascii_format_index = get_ascii_format_index(fbx_manager)
        is_initialized = exporter.Initialize(filename, ascii_format_index)
    else:
        is_initialized = exporter.Initialize(filename)

    if not is_initialized:
        raise Exception('Exporter failed to initialize. Error returned: ' + str(exporter.GetStatus().GetErrorString()))

    exporter.Export(fbx_scene)

    exporter.Destroy()


def get_ascii_format_index(fbx_manager):
    """ Obtain the index of the ASCII export format. """
    # Count the number of formats we can write to.
    num_formats = fbx_manager.GetIOPluginRegistry().GetWriterFormatCount()

    # Set the default format to the native binary format.
    format_index = fbx_manager.GetIOPluginRegistry().GetNativeWriterFormat()

    # Get the FBX format index whose corresponding description contains "ascii".
    for i in range(0, num_formats):

        # First check if the writer is an FBX writer.
        if fbx_manager.GetIOPluginRegistry().WriterIsFBX(i):

            # Obtain the description of the FBX writer.
            description = fbx_manager.GetIOPluginRegistry().GetWriterFormatDescription(i)

            # Check if the description contains 'ascii'.
            if 'ascii' in description:
                format_index = i
                break

    # Return the file format.
    return format_index


def main():
    # Get the necessary arguments
    arg_parser = optparse.OptionParser(usage='usage: %prog -i [input dir] -o [output dir] [options]',
                                       version="%prog 0.1")
    arg_parser.add_option('-o', '--output', action='store', type='string', dest='output', default=False,
                          help='FBX output file name')
    arg_parser.add_option('-i', '--input', action='store', type='string', dest='input', default=False,
                          help='The Quake 2 or VtMR map file')
    arg_parser.add_option('-t', '--textures', action='store', type='string', dest='textures', default=None,
                          help='The textures folder (optional)')
    arg_parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False,
                          help='Spews information about the process (takes more time)')

    (options, args) = arg_parser.parse_args()

    if not options.input or not options.output:
        print('Input and Output directories required to run this software!')
        arg_parser.print_version()
        arg_parser.print_help()
        quit()

    verbose = options.verbose

    if verbose:
        print('Collecting brushes from {0} and outputting into {1}'.format(options.input, options.output))

    # Create the required FBX SDK data structures.
    g_fbx_manager = fbx.FbxManager.Create()
    g_fbx_scene = fbx.FbxScene.Create(g_fbx_manager, '')

    print('Collecting entities from map file and creating polygons...')
    # Collect all of the brushes from the map file
    map_data = id_map.Id2Map()
    map_data.parse_map_file(options.input, verbose, options.textures)

    brush_index_in = 0
    print('{0} entities parsed, creating fbx'.format(len(map_data.entities)))
    # Create a scene node per brush containing the brushes UV'd mesh
    for entity_in in map_data.entities:
        brush_index_in += add_entity_to_scene(g_fbx_scene, entity_in, brush_index_in)

    # Save the scene.
    save_scene(options.output, g_fbx_manager, g_fbx_scene, True)
    #
    # Destroy the fbx manager explicitly, which recursively destroys
    # all the objects that have been created with it.
    g_fbx_manager.Destroy()
    del g_fbx_manager, g_fbx_scene


if __name__ == '__main__':
    main()
