# coding: utf-8
import sys
import os

os.environ["MAYA_SKIP_USERSETUP_PY"] = ""
from maya import standalone

sys.path.append(r'C:/Users/yuweiming/Documents/maya/2018/scripts')
standalone.initialize()


def testCacheFn( project, assetType, assetList ):
    import time
    import libraryCache as lc
    reload(lc)
    localTime = time.localtime()
    tim = '%02d%02d%02d' % (localTime.tm_hour, localTime.tm_min, localTime.tm_sec)

    cacheInfoList = {'success': [], 'failure': []}
    for asset in assetList:
        logFolder = lc.getWorkFolder('cat11', tim, asset)
        infos = {project: {assetType: {asset: 1}}}
        result = lc.batchTestAssetCacheFn(infos, tim)

        if result:
            logText, renderCmds, judge = lc.analyseLibraryResult(result)
            if judge == 2:
                cacheInfoList['success'].append(asset)

                with open('%s/result.txt' % logFolder, 'w') as f:
                    f.write(logText.encode('utf8'))
                with open('%s/renderCmd.bat' % logFolder, 'w') as f:
                    f.write(renderCmds)

        else:
            cacheInfoList['failure'].append(asset)

    infoFolder = lc.getWorkFolder('cat11', tim,'')
    with open('%s/cacheState.txt' % infoFolder, 'w') as f:
        for info, assetList in cacheInfoList.items():
            f.write('\n'+info.encode('utf8') + '\n')
            f.write('\t\t' + str(assetList))

    os.startfile(infoFolder)
    return cacheInfoList


if __name__ == '__main__':
    project = sys.argv[1]
    assetType = sys.argv[2]
    assetList = sys.argv[3:]
    testCacheFn(project, assetType, assetList)
