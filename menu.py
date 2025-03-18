# -------------------------------------------
# menu.py
# Version: 1.0
# Created by: Gonzalo Rojas
# -------------------------------------------


# ----- GLOBAL IMPORTS ---------------

import nuke
import configure_shot
import multi_import

# ----- ADDING CUSTOM MENUS --------------------------

pipeline_menu = nuke.menu('Nuke').addMenu('Pipeline')
# Task_01
pipeline_menu.addCommand('Configure Shot', "configure_shot.configure_shot()")
pipeline_menu.addCommand('Import Multiple Sequences', "multi_import.multi_import()")