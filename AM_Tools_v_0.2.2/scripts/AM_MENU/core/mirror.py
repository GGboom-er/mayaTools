"""
I've got this code from mgear Rigging system and just I 've changed a little based on my Rigging system
to get more info you can check mgear website : http://www.mgear-framework.com/
"""
import re
import maya.cmds as mc
import pymel.core as pm
from AM_MENU.core import  utils




def mirrorPose(flip=False , nodes=None):

    if nodes is None:
        nodes = pm.selected()
    
    
    mc.undoInfo(ock=1)
    try:
        nameSpace = False
        if nodes:
            nameSpace = utils.getNamespace(nodes[0])

        mirrorEntries = []
        for oSel in nodes:
            mirrorEntries.extend(gatherMirrorData(nameSpace, oSel, flip))

        for dat in mirrorEntries:
            if dat["attr"] in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
                applyMirror(nameSpace, dat)
    except Exception as e:
        pm.displayWarning("Flip/Mirror pose fail")
        import traceback
        traceback.print_exc()
        print(e)
    finally:
        mc.undoInfo(cck=1)




def applyMirror(nameSpace, mirrorEntry):
    
    node = mirrorEntry["target"]
    attr = mirrorEntry["attr"]
    val = mirrorEntry["val"]
    
    try:
        if (pm.attributeQuery(attr, node=node, shortName=True, exists=True) and not node.attr(attr).isLocked()):
            node.attr(attr).set(val)

    except RuntimeError as e:
        pass




def gatherMirrorData(nameSpace, node, flip):
    
    if isSideNode(node):
        nameParts = swapSideLabelNode(node)
        nameTarget = ":".join([nameSpace, nameParts])
        oTarget = utils.getNode(nameTarget)
        return calculateMirrorData(node, oTarget, flip=flip)
    else:
        return calculateMirrorData(node, node, flip=False)




def swapSideLabelNode(node):

    name = node.stripNamespace()
    sw_name = swapSideLabel(name)
    if name != sw_name:
        return sw_name
    
    if node.hasAttr("side_meta"):
        data = get_side_data(node)
        side = data["side"]
        if side in "LR":
            if side == "L":
                cm_side = data["R_label"]
            elif side == "R":
                cm_side = data["L_label"]
            return node.stripNamespace().replace(data["C_label"], cm_side)
        else:
            return node.stripNamespace()

    else:
        return swapSideLabel(node.stripNamespace())




def isSideNode(node):
    if node.hasAttr("side_meta"):
        data = get_side_data(node)
        if data["side"] in "LR":
            return True
        else:
            return False
    else:
        return isSideElement(node.name())




def isSideElement(name):
    if "L_" in name or "R_" in name:
        return True
    else:
        return False
        


def get_side_data(node):
    data = node.attr("side_meta").get().split("|")
    dict_data = {
        "side":data[0],
        "L_label":data[1],
        "R_label":data[2],
        "C_label":data[3],
    }
    return dict_data

        


def calculateMirrorData(srcNode, targetNode, flip=False):
    results = []

    for attrName in listAttrForMirror(srcNode):
        
        invCheckName = "inv{0}".format(attrName.lower().capitalize())
        if not pm.attributeQuery(invCheckName, node=srcNode, shortName=True, exists=True):
            inv = 1
        else:
            invAttr = srcNode.attr(invCheckName)
            inv = -1 if invAttr.get() else 1
            
        invAttrName = swapSideLabel(attrName) if isSideElement(attrName) else attrName

        if flip:
            flipVal = targetNode.attr(attrName).get()
            results.append({"target": srcNode, "attr": invAttrName, "val": flipVal * inv})
        results.append({"target": targetNode, "attr": invAttrName, "val": srcNode.attr(attrName).get() * inv})
    return results




def listAttrForMirror(node):
    res = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "ro"]
    res.extend(pm.listAttr(node, userDefined=True, shortNames=True))
    res = list([x for x in res if not x.startswith("inv")])
    res = list([x for x in res if node.attr(x).type()
                not in ["message", "string"]])
    return res





# part = name.split("_")[2]

def swapSideLabel(name):
    for part in name.split("_"):
        if re.compile("L").match(part):
            try:
                return re.compile("L_").sub(r"R_", name)
            except:
                return re.compile("_L").sub(r"_R", name)
                
        if re.compile("R").match(part):
            try:
                return re.compile("R_").sub(r"L_", name)
            except:
                return re.compile("_R").sub(r"_L", name)
                
    else:
        if "_L_" in name:
            return name.replace("_L_", "_R_")
        elif "_R_" in name:
            return name.replace("_R_", "_L_")
        else:
            return name









    
    
    