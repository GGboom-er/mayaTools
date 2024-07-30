import pymel.core as pm

def aboutAnimPicker(*args):
    """About anim_picker"""
    note = """
    
    Copyright (c) 2018 Guillaume Barlier
    https://github.com/gbarlier
    
    
    The Animation picker tool called "anim_picker" for short is a tool for Maya.
    This tool allows you to create a graphical interface for quick animation controls 
    selection.
    
    anim_picker has developed by Guillaume Barlier and mGear-Dev Organization
    
    For further info, You can check out below link:
        http://forum.mgear-framework.com/t/animpicker-how-to-use/1769
        
    Tutorials:
        https://www.youtube.com/watch?v=uQFLg8cWKb0
        https://www.youtube.com/watch?v=7XQrnBn2pIo
    
    
    """
    pm.confirmDialog(title='About anim_picker', message=note, button=["OK"],
                     defaultButton='OK', cancelButton='OK', dismissString='OK')

