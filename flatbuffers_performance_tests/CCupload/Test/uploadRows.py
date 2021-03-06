# automatically generated by the FlatBuffers compiler, do not modify

# namespace: Test

import flatbuffers

class uploadRows(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsuploadRows(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = uploadRows()
        x.Init(buf, n + offset)
        return x

    # uploadRows
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # uploadRows
    def Rows(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 32
            from .rowObject import rowObject
            obj = rowObject()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # uploadRows
    def RowsLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

def uploadRowsStart(builder): builder.StartObject(1)
def uploadRowsAddRows(builder, rows): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(rows), 0)
def uploadRowsStartRowsVector(builder, numElems): return builder.StartVector(32, numElems, 8)
def uploadRowsEnd(builder): return builder.EndObject()
