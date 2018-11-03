# automatically generated by the FlatBuffers compiler, do not modify

# namespace: Test

import flatbuffers

class row_object(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsrow_object(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = row_object()
        x.Init(buf, n + offset)
        return x

    # row_object
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # row_object
    def RowKey(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # row_object
    def Datapoint(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            x = self._tab.Indirect(o + self._tab.Pos)
            from .data import data
            obj = data()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

def row_objectStart(builder): builder.StartObject(2)
def row_objectAddRowKey(builder, rowKey): builder.PrependInt32Slot(0, rowKey, 0)
def row_objectAddDatapoint(builder, datapoint): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(datapoint), 0)
def row_objectEnd(builder): return builder.EndObject()