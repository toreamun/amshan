import fastframecheck


class HdlcFrame:
    _buffer = None
    _ffc = None

    def __init__(self):
        self._buffer = bytearray()
        self._ffc = fastframecheck.FastFrameCheckSequence()

    def __len__(self):
        return len(self._buffer)

    def append(self, byte):
        self._buffer.append(byte)
        self._ffc.update(byte)
        if self._ffc.is_good:
            print("Is final")



class HdlcOctetStuffedFrameReader:
    CONTROL_ESCAPE = b'\x7d'
    FLAG_SEQUENCE = b'\x7e'

    def __init__(self):
        self._buffer = bytearray()
        self._buffer_pos = 0
        self._frame = None

    def read(self, data):
        self._buffer.extend(data)

        if self._frame is None:
            flag_pos = self._buffer.find(self.FLAG_SEQUENCE)
            if flag_pos == -1:
                # flag sequence not found
                self._buffer.clear()
            if flag_pos >= 0:
                if flag_pos > 0:
                    # trim data before flag sequence
                    self._buffer = self._buffer[flag_pos:]
                self._frame = HdlcFrame()
            self._buffer_pos = 0

        if len(self._buffer) > 0:
            while self._buffer_pos < len(self._buffer):
                current = self._buffer[self._buffer_pos]
                print(hex(current))

                if current == self.FLAG_SEQUENCE[0]:
                    print("FOUND flag seq")
                    if len(self._frame) > 0:
                        print("END of frame")
                        self._frame = HdlcFrame()
                        self._buffer = self._buffer[self._buffer_pos:]
                        self._buffer_pos = 0
                    else:
                        print("START of frame")
                else:
                    if current == self.CONTROL_ESCAPE[0]:
                        print("FOUND control escape")

                    self._frame.append(current)

                self._buffer_pos += 1
