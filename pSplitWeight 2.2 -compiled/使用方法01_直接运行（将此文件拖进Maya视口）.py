#coding=utf-8
try:
    from importlib import reload
except:
    from imp import reload
finally:
    pass

def run():
    import pSplitWeight # 这里不能用 from . import pEdgeWeight，因为并不是在一个已导入的包内部运行这个模块，即使这个模块的所在路径加进了sys.path也是不行的
    reload (pSplitWeight) 

def onMayaDroppedPythonFile(param):
    run() 