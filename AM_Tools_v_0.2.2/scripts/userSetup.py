import importlib
import AM_MENU
import AM_MENU.core.chbox
from pymel import mayautils

mayautils.executeDeferred(AM_MENU.AM_toolsMenuLoader)
mayautils.executeDeferred(AM_MENU.UpdateChecker)
