from pickletools import read_stringnl_noescape_pair

import nuke
import os


def create_backdrop(nodes, title="", tile_color=0x9bff, font_size=21, ofst=100):
    """Creates a Nuke Backdrop node around the given nodes.

    This function places a backdrop behind the specified nodes, adjusting its
    size to encompass them with an offset. It also sets a title, color, and font
    properties for the backdrop.

    Args:
        nodes (list of nuke.Node): The nodes to be enclosed within the backdrop.
        title (str, optional): The title displayed on the backdrop. Defaults to "".
        tile_color (int, optional): The color of the backdrop tile in hexadecimal.
            Defaults to 0x9bff.
        font_size (int, optional): The font size of the backdrop label. Defaults to 21.
        ofst (int, optional): The padding around the enclosed nodes. Defaults to 100.

    Returns:
        nuke.Node: The created BackdropNode.

    Raises:
        ValueError: If the `nodes` list is empty.
    """
    # Deselect all nodes
    nuke.selectAll()
    nuke.invertSelection()

    # Html title tags
    label = "<p align='center'><font color='black'>{}</font></p>".format(title)

    if not nodes:
        raise ValueError("The 'nodes' list cannot be empty.")

    for node in nodes:
        node.setSelected(True)

    # Calculate bounds
    sel = nuke.selectedNodes()
    bdX = min([node.xpos() for node in sel])
    bdY = min([node.ypos() for node in sel])
    bdW = max([node.xpos() + node.screenWidth() for node in sel]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in sel]) - bdY

    # Backdrop offset
    left, top, right, bottom = (-ofst, -(ofst * 2), ofst, ofst)
    bdX += left
    bdY += top
    bdW += (right - left)
    bdH += (bottom - top)

    # Create Backdrop node
    bckDp = nuke.nodes.BackdropNode(
        xpos=bdX, bdwidth=bdW, ypos=bdY, bdheight=bdH, note_font_size=30
    )
    bckDp['label'].setValue(label)
    bckDp['note_font'].setValue("Verdana Bold")
    bckDp['note_font_size'].setValue(font_size)
    bckDp['tile_color'].setValue(tile_color)

    for node in nodes:
        node.setSelected(False)

    return bckDp

def create_read_node(folder_path):
    """Creates a Nuke Read node from a sequence of images in the specified folder.

    This function retrieves the first file in the folder, extracts the frame range,
    constructs the proper file path format for Nuke, and creates a Read node with
    the appropriate settings.

    Args:
        folder_path (str): The directory containing the image sequence.

    Returns:
        nuke.Node: The created Read node.

    Raises:
        IndexError: If the folder is empty or does not contain a valid sequence.
        ValueError: If the frame range format is incorrect.
        OSError: If there are issues accessing the folder or files.
    """
    folder_info = nuke.getFileNameList(folder_path)
    file_name, frame_range = folder_info[0].split(" ")
    first_frame, last_frame = frame_range.split("-")
    first_frame = int(first_frame)
    last_frame = int(last_frame)
    digit_count = len(str(abs(last_frame)))
    hash_string = "#" * digit_count
    new_filename = file_name.replace("#", hash_string)
    file_path = os.path.join(folder_path, new_filename)
    file_path = os.path.normpath(file_path)
    file_path = file_path.replace("\\", "/")

    # create read node
    read_node = nuke.createNode("Read", inpanel=False)
    read_node["file"].setValue(file_path)
    read_node["first"].setValue(first_frame)
    read_node["last"].setValue(last_frame)
    read_node["origfirst"].setValue(first_frame)
    read_node["origlast"].setValue(last_frame)

    return read_node


def get_file_folders(folder_list, extensions):
    valid_folders = set()

    for folder in folder_list:
        if not os.path.isdir(folder):
            print("Skipping invalid folder:", folder)
            continue

        for root, _, files in os.walk(folder):
            if any(file.lower().endswith(extensions) for file in files):
                valid_folders.add(os.path.normpath(root))

    return list(valid_folders)



def import_from_list(folder_list):
    file_extensions = (".exr", ".dpx", ".jpeg", ".png")
    folders_found = get_file_folders(folder_list, file_extensions)

    node_offset = 250
    last_xpos = 0
    first_ypos = 0
    read_nodes = []

    for index, folder in enumerate(folders_found):
        read_node = create_read_node(folder)
        read_xpos = int(read_node.xpos())
        read_ypos = int(read_node.ypos())

        if index == 0:
            first_ypos = read_ypos

        last_xpos = read_xpos if index == 0 else last_xpos + node_offset
        read_node.setXYpos(last_xpos, first_ypos)

        read_nodes.append(read_node)
        create_backdrop(read_nodes,tile_color=0x46a2ff, font_size=42, title="Sequences", ofst=80)



def multi_import():
    folder_list = nuke.getFilename("Select your folders", multiple=True)

    if folder_list is None:
        print("Cancelled...")
        return

    if folder_list != [""]:
        import_from_list(folder_list)
    else:
        nuke.message("Please select at least one folder to proceed.")

if __name__ == "__main__":
    multi_import()
