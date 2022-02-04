[![GitHub Release](https://img.shields.io/github/release/toreamun/amshan?style=for-the-badge)](https://github.com/toreamun/amshan/releases)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/toreamun/amshan.svg?logo=lgtm&logoWidth=18&style=for-the-badge)](https://lgtm.com/projects/g/toreamun/amshan/context:python)
[![License](https://img.shields.io/github/license/toreamun/amshan?style=for-the-badge)](LICENSE)

![Project Maintenance](https://img.shields.io/badge/maintainer-Tore%20Amundsen%20%40toreamun-blue.svg?style=for-the-badge)
[![buy me a coffee](https://img.shields.io/badge/If%20you%20like%20it-Buy%20me%20a%20coffee-orange.svg?style=for-the-badge)](https://www.buymeacoffee.com/toreamun)

# AMSHAN

Package to help decode smart power meter data stream of IEC 62056-21 Mode D P1 or DLMS/Cosem HDLC frames used by MBUS (Meter Bus). The package can both help reading frames of meter data and/or decoding them.

The package has special support for DLMS formats used by Aidon, Kaifa and Kamstrum smart meteres (HAN) in Norway (See https://www.nek.no/info-ams-han-utviklere/) and Sweden. The Swedish P1 format format is also supported.

## Reading asynchronous from a stream of data

SmartMeterMessagePayloadProtocol can be used to read smart meter P1 date readout (ascii) or MBUS HDLC (binary) frames asynchronous. The content of each mdssage (no headers and control characters) is passed as bytes to a Queue. Headers are checked and checksum validated, and only content from non empty frames with expected length (only DLMS) and checksum is passed to the queue.

SmartMeterMessageProtocol can be used to read smart meter P1 data readout (ascii) or MBUS HDLC frames asynchronous. The complete message is sent to a Queue as an instance of as subclass of MeterReaderBase. Frames are not validated. This class is a more low level alternative to SmartMeterMessagePayloadProtocol. This type has to be used to get the meter type from P1 readouts as this is part of the message "header".

Both SmartMeterMessagePayloadProtocol and SmartMeterMessageProtocol is a [Python asyncio protocol](https://docs.python.org/3/library/asyncio-protocol.html#protocols). Protocols support different types of transports like network and serial.

It is recommended to use provided ConnectionManager and connection factories to read the data stream.

### Create protocol using transport

Pass a factory for the selected protocol (SmartMeterMessagePayloadProtocol or SmartMeterMessageProtocol) to a utility function of your selected transport (e.g., EventLoop.create_connection() for TCP/IP or serial_asyncio.create_serial_connection() for serial).

Serial example:

```python
transport, protocol = await serial_asyncio.create_serial_connection(loop, lambda: SmartMeterMessagePayloadProtocol(queue, [ModeDReader]), url = "/dev/tty01")
```

Serial example:

```python
transport, protocol = await serial_asyncio.create_serial_connection(loop, lambda: SmartMeterMessagePayloadProtocol(queue, [ModeDReader]), url = "/dev/tty01")
```

### Create protocol using provided factories

Multiple factories are provided to create a protocol as an alternative to using selected transports create function as above. Use [serial_connection_factory](serial_connection_factory.py) for serial and [tcp_connection_factory](tcp_connection_factory) for TCP/IP.

| Factory module            | SmartMeterMessageProtocol                  | SmartMeterMessagePayloadProtocol        |
| ------------------------- | ------------------------------------------ | --------------------------------------- |
| serial_connection_factory | create_serial_message_payload_connection() | create_serial_message_connection()      |
| tcp_connection_factory    | create_tcp_message_connection()            | create_tcp_message_payload_connection() |

Example of creating a SmartMeterMessagePayloadProtocol serial connection on device /dev/ttyUSB0:

```python
queue = Queue()
loop = asyncio.get_event_loop()
transport, protocol = await create_serial_frame_content_connection(queue, loop, None, url="/dev/ttyUSB0", baudrate=2400, parity=N)
```

Example of creating a SmartMeterMessageProtocol protocol TCP/IP connection to host 192.168.1.1 on port 1234:

```python
queue = Queue()
loop = asyncio.get_event_loop()
transport, protocol = await create_tcp_frame_connection(queue, loop, None, "192.168.1.1", 1234)
```

See [reader_async.py](reader_async.py) for a complete example.

### Create resilient connection with ConnectionManager

ConnectionManager maintain connection and reconnect if connection is lost. A back-off retry strategy is used when reconnecting, and a simple circuit breaker is used for lost connection.

```python
queue = Queue()
loop = asyncio.get_event_loop()
connection_manager = ConnectionManager(lambda: create_serial_message_connection(queue, loop, None, url="/dev/ttyUSB0", baudrate=2400, parity=N))
await connection_manager.connect_loop()
```

See [reader_async.py](amshan/reader_async.py) for a complete example.

## Parse P1 readouts directly from raw bytes

dlde.ModeDReader can be used to read readout by readout from bytes. Call read() to read readouts as more bytes become available. The function takes bytes as an argument and returns a list of DataReadout (the list can be empty). The function can receive incomplete readout in the buffer input and add incomplete data to an internal buffer. The buffer is schrinked when complete readout are found and returned. You should check if returned readouts are valid with readout.is_valid before using them.

## Parse frames directly from raw bytes

hdlc.HdlcFrameReader can be used to read frame by frame from bytes. Call read() to read frames as more bytes become available. The function takes bytes as an argument and returns a list of HdlcFrame (the list can be empty). The function can receive incomplete frames in the buffer input and add incomplete data to an internal buffer. The buffer is schrinked when complete frames are found and returned. You should check if returned frames are valid with frame.is_valid before using them.

# Decode norwegian and swedish messages

P1 readout and MBUS frames using the norwegian or swedish DMLS AMS format can be parsed into meter specific objects or decoded into a common dictionary. Modules exists for P1 (generic format), Aidon, Kaifa and Kamstrup meters, but the easiest is to use [autodecoder.AutoDecode](amshan/autodecode.py) to automatically detect meter type and decode the frame into a dictionary. The dictionay content is as far as possible common between meters. Possible dictionary keys kan be found as constants in [obis_map.py](amshan/obis_map.py).

Example:

```python
decoder = AutoDecoder()
frame = bytes.fromhex("e6e700" "0f" "40000000" "00" "0101" "020309060100010700ff060000011802020f00161b")
decoded = decoder.decode_frame_content(frame)
```
