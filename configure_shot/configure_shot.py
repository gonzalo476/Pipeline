import nuke

"""
Colors:
plate = 0x55994d00
denoised = 0x85994dff
"""


def create_backdrop(nodes, title="", tile_color=0x9bff, font_size=21):
    """
    Creates a backdrop node around the given nodes in Nuke.

    This function selects the provided nodes, calculates their bounding box,
    and creates a `BackdropNode` behind them with a customizable title, color,
    and font size.

    Args:
        nodes (list[nuke.Node]): List of Nuke nodes to be enclosed within the backdrop.
        title (str, optional): The title displayed inside the backdrop. Defaults to an empty string.
        tile_color (int, optional): Hexadecimal color for the backdrop. Defaults to `0x9bff`.
        font_size (int, optional): Font size for the backdrop label. Defaults to `21`.

    Returns:
        nuke.Node: The created `BackdropNode`.
    """

    # deselect nodes
    nuke.selectAll()
    nuke.invertSelection()

    # Html title tags
    label = "<p align='center'><font color='black'>{}</font></p>".format(title)

    for node in nodes:
        node.setSelected(True)

    # calc bounds
    sel = nuke.selectedNodes()
    bdX = min([node.xpos() for node in sel])
    bdY = min([node.ypos() for node in sel])
    bdW = max([node.xpos() + node.screenWidth() for node in sel]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in sel]) - bdY

    # backdrop offset
    ofst = 100
    left, top, right, bottom = (-ofst, -(ofst * 2), ofst, ofst)
    bdX += left
    bdY += top
    bdW += (right - left)
    bdH += (bottom - top)
    bckDp = nuke.nodes.BackdropNode(xpos=bdX, bdwidth=bdW, ypos=bdY, bdheight=bdH, note_font_size=30)
    bckDp['label'].setValue(label)
    bckDp['note_font'].setValue("Verdana Bold")
    bckDp['note_font_size'].setValue(font_size)
    bckDp['tile_color'].setValue(tile_color)

    for node in nodes:
        node.setSelected(False)

    return bckDp


def configure_shot():
    """
    Sets the root settings based on the selected 'Read' node.
    """

    read_node = nuke.selectedNode()

    if read_node.Class() != "Read":
        nuke.message("Selected node is not a Read node. Please select a valid Read node.")
        return

    # Get Read node values
    node_first_frame = read_node["first"].getValue()
    node_last_frame = read_node["last"].getValue()
    node_format = read_node["format"].value()
    node_metadata = read_node.metadata()
    node_filetype = node_metadata.get("input/filereader")
    node_frame_rate = node_metadata.get("input/frame_rate")
    node_frame_rate = round(node_frame_rate, 3)
    node_xpos = int(read_node.xpos())
    node_ypos = int(read_node.ypos())

    # Calc new frame range
    new_start_frame = 1001
    total_frames = int(node_last_frame) - int(node_first_frame) + 1
    new_end_frame = new_start_frame + (total_frames - 1)

    # Set the Read node
    read_node["frame_mode"].setValue("start at")
    read_node["frame"].setValue(str(new_start_frame))

    # Set the Root
    nuke.root()["first_frame"].setValue(new_start_frame)
    nuke.root()["last_frame"].setValue(new_end_frame)
    nuke.root()["frame"].setValue(new_start_frame)
    nuke.root()["format"].setValue(node_format)
    nuke.root()["fps"].setValue(node_frame_rate)
    nuke.root()["lock_range"].setValue(True)

    # Set backdrop node
    create_backdrop([read_node], "PLATE", 0x55994d00, 62)

    # Create postage stamp
    postage_stamp = nuke.createNode("PostageStamp", inpanel=False)
    postage_stamp.setXYpos(node_xpos + 480, node_ypos - 20)
    postage_stamp.setInput(0, read_node)
    postage_stamp["name"].setValue("_PLATE_")
    postage_stamp["tile_color"].setValue(0xff)
    postage_stamp["hide_input"].setValue(True)
    postage_stamp_xpos = int(postage_stamp.xpos())
    postage_stamp_ypos = int(postage_stamp.ypos())

    # Create denoiser
    denoiser = nuke.createNode("OFXcom.absoft.neatvideo4_v4", inpanel=False)
    denoiser.setXYpos(postage_stamp_xpos, postage_stamp_ypos + 80)
    denoiser.setInput(0, postage_stamp)

    # Create denoise backdrop
    create_backdrop([postage_stamp, denoiser], "DENOISE", 0x85994dff, 62)


if __name__ == "__main__":
    configure_shot()
