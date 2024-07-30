import sys
import types


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY34 = sys.version_info[0:2] >= (3, 4)


if PY2:
    class Object(object):
        pass
    
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str
    
else:
    class Object:
        pass

    string_types = str,
    integer_types = int,
    class_types = type,
    text_type = str
    binary_type = bytes










