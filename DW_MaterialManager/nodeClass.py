#encoding:utf-8
import maya.cmds as mc

class NodeAttr(object):
    def __init__(self,attr_v3):
        self.nodeName = attr_v3.rpartition('.')[0]
        self.attrName = attr_v3.rpartition('.')[2]
        self.fullName = attr_v3
    def __str__(self):
        return self.fullName
    def __plusMinusNodeSet(self,other,plusMinusNode):
        if 'NodeAttr' in str(type(other)):
            try:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0]')
            except:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dx')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dy')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dz')
            try:
                mc.connectAttr(other.fullName,plusMinusNode + '.input3D[1]')
            except:
                mc.connectAttr(other.fullName,plusMinusNode + '.input3D[1].input3Dy')
                mc.connectAttr(other.fullName,plusMinusNode + '.input3D[1].input3Dx')
                mc.connectAttr(other.fullName,plusMinusNode + '.input3D[1].input3Dz')
        elif isinstance(other,float) or isinstance(other,int):
            try:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0]')
            except:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dx')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dy')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dz')
            mc.setAttr(plusMinusNode + '.input3D[1].input3Dx' ,other)
            mc.setAttr(plusMinusNode + '.input3D[1].input3Dy' ,other)
            mc.setAttr(plusMinusNode + '.input3D[1].input3Dz' ,other)
        elif isinstance(other,list) or isinstance(other,tuple):
            try:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0]')
            except:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dx')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dy')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dz')
            mc.setAttr(plusMinusNode + '.input3D[1].input3Dx' ,other[0])
            mc.setAttr(plusMinusNode + '.input3D[1].input3Dy' ,other[1])
            mc.setAttr(plusMinusNode + '.input3D[1].input3Dz' ,other[2])
    def __rplusMinusNodeSet(self,other,plusMinusNode):
        if 'NodeAttr' in str(type(other)):
            try:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[1]')
            except:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[1].input3Dx')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[1].input3Dy')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[1].input3Dz')
            try:
                mc.connectAttr(other.fullName,plusMinusNode + '.input3D[0]')
            except:
                mc.connectAttr(other.fullName,plusMinusNode + '.input3D[0].input3Dx')
                mc.connectAttr(other.fullName,plusMinusNode + '.input3D[0].input3Dy')
                mc.connectAttr(other.fullName,plusMinusNode + '.input3D[0].input3Dz')
        elif isinstance(other,float) or isinstance(other,int):
            try:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[1]')
            except:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[1].input3Dx')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[1].input3Dy')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[1].input3Dz')
            mc.setAttr(plusMinusNode + '.input3D[0].input3Dx' ,other)
            mc.setAttr(plusMinusNode + '.input3D[0].input3Dy' ,other)
            mc.setAttr(plusMinusNode + '.input3D[0].input3Dz' ,other)
        elif isinstance(other,list) or isinstance(other,tuple):
            try:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0]')
            except:
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dx')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dy')
                mc.connectAttr(self.fullName,plusMinusNode + '.input3D[0].input3Dz')
            mc.setAttr(plusMinusNode + '.input3D[0].input3Dx' ,other[0])
            mc.setAttr(plusMinusNode + '.input3D[0].input3Dy' ,other[1])
            mc.setAttr(plusMinusNode + '.input3D[0].input3Dz' ,other[2])
    def __add__(self,other):
        #create the plus node
        plusNode = mc.shadingNode('plusMinusAverage',au = 1,n = 'plus')
        mc.setAttr(plusNode + '.operation',1)
        self.__plusMinusNodeSet(other,plusNode)
        return NodeAttr(plusNode + '.output3D')
    def __sub__(self,other):
        minusNode = mc.shadingNode('plusMinusAverage',au = 1,n = 'minus')
        mc.setAttr(minusNode + '.operation',2)
        self.__plusMinusNodeSet(other,minusNode)
        return NodeAttr(minusNode + '.output3D')
    def __radd__(self,other):
        #create the plus node
        plusNode = mc.shadingNode('plusMinusAverage',au = 1,n = 'plus')
        mc.setAttr(plusNode + '.operation',1)
        self.__rplusMinusNodeSet(other,plusNode)
        return NodeAttr(plusNode + '.output3D')
    def __rsub__(self,other):
        minusNode = mc.shadingNode('plusMinusAverage',au = 1,n = 'minus')
        mc.setAttr(minusNode + '.operation',2)
        self.__rplusMinusNodeSet(other,minusNode)
        return NodeAttr(minusNode + '.output3D')


    def __multiplyDivideNodeSet(self,other,multiplyDivideNode):
        if 'NodeAttr' in str(type(other)):
            try:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1')
            except:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1.input1X')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1.input1Y')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1.input1Z')
            try:
                mc.connectAttr(other.fullName,multiplyDivideNode + '.input2')
            except:
                mc.connectAttr(other.fullName,multiplyDivideNode + '.input2.input2X')
                mc.connectAttr(other.fullName,multiplyDivideNode + '.input2.input2Y')
                mc.connectAttr(other.fullName,multiplyDivideNode + '.input2.input2Z')
        elif isinstance(other,float) or isinstance(other,int):
            try:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1')
            except:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1.input1X')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1.input1Y')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1.input1Z')
            mc.setAttr(multiplyDivideNode + '.input2X',other)
            mc.setAttr(multiplyDivideNode + '.input2Y',other)
            mc.setAttr(multiplyDivideNode + '.input2Z',other)
        elif isinstance(other,list) or isinstance(other,tuple):
            try:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1')
            except:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1.input1X')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1.input1Y')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input1.input1Z')
            mc.setAttr(multiplyDivideNode + '.input2X' ,other[0])
            mc.setAttr(multiplyDivideNode + '.input2Y' ,other[1])
            mc.setAttr(multiplyDivideNode + '.input2Z' ,other[2])
    def __rmultiplyDivideNodeSet(self,other,multiplyDivideNode):
        if 'NodeAttr' in str(type(other)):
            try:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2')
            except:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2.input2X')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2.input2Y')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2.input2Z')
            try:
                mc.connectAttr(other.fullName,multiplyDivideNode + '.input1')
            except:
                mc.connectAttr(other.fullName,multiplyDivideNode + '.input1.input1X')
                mc.connectAttr(other.fullName,multiplyDivideNode + '.input1.input1Y')
                mc.connectAttr(other.fullName,multiplyDivideNode + '.input1.input1Z')
        elif isinstance(other,float) or isinstance(other,int):
            try:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2')
            except:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2.input2X')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2.input2Y')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2.input2Z')
            mc.setAttr(multiplyDivideNode + '.input1X',other)
            mc.setAttr(multiplyDivideNode + '.input1Y',other)
            mc.setAttr(multiplyDivideNode + '.input1Z',other)
        elif isinstance(other,list) or isinstance(other,tuple):
            try:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2')
            except:
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2.input2X')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2.input2Y')
                mc.connectAttr(self.fullName,multiplyDivideNode + '.input2.input2Z')
            mc.setAttr(multiplyDivideNode + '.input1X' ,other[0])
            mc.setAttr(multiplyDivideNode + '.input1Y' ,other[1])
            mc.setAttr(multiplyDivideNode + '.input1Z' ,other[2])    

    def __mul__(self,other):
        multiplyNode = mc.shadingNode('multiplyDivide',au = 1, n = 'multiply')
        mc.setAttr(multiplyNode + '.operation',1)
        self.__multiplyDivideNodeSet(other,multiplyNode)
        return NodeAttr(multiplyNode + '.output')
    def __rmul__(self,other):
        multiplyNode = mc.shadingNode('multiplyDivide',au = 1, n = 'multiply')
        mc.setAttr(multiplyNode + '.operation',1)
        self.__rmultiplyDivideNodeSet(other,multiplyNode)
        return NodeAttr(multiplyNode + '.output')
    def __div__(self,other):
        divideNode = mc.shadingNode('multiplyDivide',au = 1, n = 'divide')
        mc.setAttr(divideNode + '.operation',2)
        self.__multiplyDivideNodeSet(other,divideNode)
        return NodeAttr(divideNode + '.output')
    def __rdiv__(self,other):
        divideNode = mc.shadingNode('multiplyDivide',au = 1, n = 'divide')
        mc.setAttr(divideNode + '.operation',2)
        self.__rmultiplyDivideNodeSet(other,divideNode)
        return NodeAttr(divideNode + '.output')
    def __pow__(self,other):
        #create the power node
        powNode = mc.shadingNode('multiplyDivide',au = 1,n = 'pow')
        mc.setAttr(powNode + '.operation',3)
        self.__multiplyDivideNodeSet(other,powNode)
        return NodeAttr(powNode + '.output')
