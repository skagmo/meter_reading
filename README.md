# Aidon/Hafslund AMS parsing code

Use with an M-Bus dongle such as [this one](https://www.aliexpress.com/item/USB-to-MBUS-slave-module-MBUS-master-slave-communication-debugging-bus-monitor-TSS721-No-spontaneity-Self/32894249052.html).

Parser class (aidon_obis.py) requires crcmod (sudo pip install crcmod).

### aidon_test.py
Test output
./aidon_test.py <port>
./aidon_test.py /dev/ttyUSB0

### aidon_influxdb_forward.py
Forward to influxdb.
./aidon_influxdb_forward.py <port> <influxdb API address> <database>
./aidon_influxdb_forward.py /dev/ttyUSB0 http://localhost:8086 metering

### aidon_read.py
Parses preliminary protocol used by Hafslund. 
"./aidon_read.py /dev/ttyUSB0"
