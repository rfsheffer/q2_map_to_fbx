__author__ = 'Ryan'

import optparse
import fbx
import id_map

def add_entity_to_scene(scene, entity, brush_index):
    """
    Adds a brush as a scene node
    :param scene: The scene to add to
    """

    # Obtain a reference to the scene's root node.
    root_node = scene.GetRootNode()

    # Create a new node in the scene.
    new_node = fbx.FbxNode.Create(scene, 'brushNode{0}'.format(brush_index))
    root_node.AddChild(new_node)

    # Create a new mesh node attribute in the scene, and set it as the new node's attribute
    new_mesh = fbx.FbxMesh.Create(scene, 'brushMesh'.format(brush_index))
    new_node.SetNodeAttribute(new_mesh)


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


if __name__ == '__main__':

    # Get the necessary arguments
    argParser = optparse.OptionParser(usage='usage: %prog [options]')
    argParser.add_option('-o', '--output', action='store', type='string', dest='output', default='default_out.fbx',
                         help='FBX output file name')
    argParser.add_option('-i', '--input', action='store', type='string', dest='input', default=False,
                         help='The VtMR map file')

    (options, args) = argParser.parse_args()

    print('Collecting brushes from {0} and outputting into {1}'.format(options.input, options.output))

    # Create the required FBX SDK data structures.
    g_fbx_manager = fbx.FbxManager.Create()
    g_fbx_scene = fbx.FbxScene.Create(g_fbx_manager, '')

    # Collect all of the brushes from the map file
    map_data = id_map.Id2Map()
    map_data.parse_map_file(options.input)

    # Create a scene node per brush containing the brushes UV'd mesh
    for entity in map_data.entities:
        add_entity_to_scene(g_fbx_scene, entity, 0)

    # Save the scene.
    save_scene(options.output, g_fbx_manager, g_fbx_scene, True)
    #
    # Destroy the fbx manager explicitly, which recursively destroys
    # all the objects that have been created with it.
    g_fbx_manager.Destroy()
    del g_fbx_manager, g_fbx_scene
