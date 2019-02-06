# Aidon/Hafslund AMS parsing code

Use with an M-Bus dongle such as [this one](https://www.aliexpress.com/item/USB-to-MBUS-slave-module-MBUS-master-slave-communication-debugging-bus-monitor-TSS721-No-spontaneity-Self/32894249052.html).

Parser class (aidon_obis.py) requires python module crcmod (sudo pip install crcmod).

NB: This is not a full COSEM parser, as the number of OBIS fields and their sequence is assumed to be as on a Hafslund meter.

### aidon_test.py
Test output <br/>
./aidon_test.py <port> <br/>
./aidon_test.py /dev/ttyUSB0 <br/>

### aidon_influxdb_forward.py
Forward to influxdb. <br/>
./aidon_influxdb_forward.py <port> <influxdb API address> <database> <br/>
./aidon_influxdb_forward.py /dev/ttyUSB0 http://localhost:8086 metering <br/>

### aidon_read.py
Parses preliminary protocol used by Hafslund. <br/>
"./aidon_read.py /dev/ttyUSB0" <br/>
