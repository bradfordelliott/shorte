@doctitle Simple
@docsubtitle Some Shorte Examples
@docnumber 23456
@docfilename blah_blah

@docrevisions
- Version | Date           | Description
- 1.0     | 04 March, 2011 | Blah blah blah, this is something here describing the revision
- 1.4.0   | 05 March, 2011 | Something else
- 1.4.4   | 06 March, 2011 | This is a really long description of the version
                             change here and what changed in the document. It doesn't
                             match the format of the document but whatever.

@body

@h1 Test Results
This is a simple example where I don't need the
text tag.

@{hl,This is some text here} and some more @{hl,text here} and some @{bold,Blah blah blah}

@enum: name="e_my_test" caption="This is a test enum"
- Name | Value | Description
- LEEDS_VLT_SUPPLY_1V_TX | 0x0 |  1V supply TX 
- LEEDS_VLT_SUPPLY_1V_RX | 0x1 |  1V supply RX 
- LEEDS_VLT_SUPPLY_1V_CRE | 0x2 |  1V supply digital core 
- LEEDS_VLT_SUPPLY_1V_DIG_RX | 0x3 |  1V supply digital RX 
- LEEDS_VLT_SUPPLY_1p8V_RX | 0x4 |  1.8V supply RX 
- LEEDS_VLT_SUPPLY_1p8V_TX | 0x5 |  1.8V supply TX 
- LEEDS_VLT_SUPPLY_2p5V | 0xf |  2.5V supply 
- LEEDS_VLT_SUPPLY_TP_P | 0x9 |  Test point P 
- LEEDS_VLT_SUPPLY_TP_N | 0x8 |  Test point N 

@table: title="blah2" caption="blah blah"
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number

@struct: title="blah2" caption="blah blah" diagram="show:yes,align:128,bitorder:decrement"
- Field | Name          | Description
- 8x8   | serial_number | The serial number of the device
                          with some more description
- 8x12  | part_number   | The part number of the device
- 4     | some_number   | Some random 4 byte number
@h2: if="1"
This is a test
With some more data

# In the table below we'll use the || sequence
# to span columns. The 'one' field will
# automatically span columns.
@table: title="Blah blah" mark_reserved="true"
- Header    ||     | Blah | Blah
- one
-* two
-& three
- two       | two
-
- three     ||     | XXX  | tmp
- Reserved  ||     | XXX  | tmp


@table
- Header    ||     | Blah | Blah
- one
-* two
-& three
- two       | two
-
- three     ||     | XXX  | tmp
- Reserved  ||     | XXX  | tmp


@sequence: title="Two Step Master" caption="Two Step Master Behavior"
- Type    | Source       | Sink              | Name                   | Description

# Two-Step Sync Message
- message | Master NPU   | Master PHY        | Sync Message           | The master NPU constructs a Sync Message to send to
                                                                        any slaves. It sets the twoStepFlag in the
                                                                        flagField field of the PTP header to indicate that this is a two
                                                                        step message and sets the originTimestamp and
                                                                        correctionFields to zero. It then generates a unique ID that
                                                                        uniquely identifies the PTP session
                                                                        and writes it to the 32 bit reserved field in the header
                                                                        and sets the extraction flag.
                                                                        This unique ID
                                                                        is used by the h/w to cache the departure timestamp (T1).
                                                                        The master then sends the Sync Message via the egress path of the h/w.
- action  | Master PHY   |                   | Process Sync           | The egress path of the h/w receives the two-step
                                                                        sync message and sees the twoStepFlag asserted. It
                                                                        extracts the Unique ID from the 32 bit reserved field and records the
                                                                        timewheel value of (T1) of the outbound sync message and pushes it
                                                                        to the egress timestamp FIFO. It then zeros the reserved field
                                                                        before forwarding the message.
- message | Master PHY   | Slave PHY         | Sync Message           | The h/w in the master forwards the Sync message to the
                                                                        h/w in the slave.
- message | Slave PHY    | Slave NPU         | Sync Message           | The slave receives the Sync message. It extracts the
                                                                        arrival timestamp of the sync message based on its current
                                                                        timewheel value and places it in the 32 bit reserved field of
                                                                        the header and forwards the sync message to the slave NPU. This
                                                                        is the T2 timestamp. The slave saves the T2 timestamp for later
                                                                        lookup.

# Two-Step Follow up Message
- message | Master NPU   | Master PHY        | Follow Up Message      | The master constructs a follow up message. It extracts the
                                                                        timestamp of the original sync message (T1) from the h/w
                                                                        and places it in the preciseOriginTimestamp field. It clears
                                                                        the extraction flag in the 32 bit reserved field so that the h/w
                                                                        will not attempt to capture the timestamp. It then sends
                                                                        the message to the Leeds master h/w to forward to the slave. It
                                                                        sets the twoStepFlag bit in the header (is this necessary?)
- message | Master PHY   | Slave PHY         | Follow Up Message      | The master h/w forwards the message to the slave h/w
                                                                        across the network. The extraction bit in the reserved field is not
                                                                        set so no timestamp is recorded.
- message | Slave PHY    | Slave NPU         | Follow Up Message      | The slave h/w receives the follow up message from the h/w. It
                                                                        updates the 32 bit reserved field in the header with the timestamp
                                                                        of the message arrival. This information is not required. It forwards
                                                                        the message to the NPU for processing.
- action  | Slave NPU    |                   | Record T1 & T2         | The slave NPU receives the Follow Up Message and records the T1
                                                                        timestamp from the preciseOriginTimestamp field of Follow Up message.
                                                                        It also looks up the arrival time it saved when it received the original sync message (T2).



# Delay Request Message
- message | Slave NPU    | Slave PHY         | Delay Request Message  | The slave constructs a send delay request messag. It generates a 16 bit unique ID
                                                                        and writes it to the 32 bit reserved field of the header. The unique ID must
                                                                        be albe to uniquely identify the PTP stream upon receipt of the Delay Response Message. It
                                                                        also sets the extraction field in the reserved field of the header to tell the PHY
                                                                        to extract the departure timestamp (T3). It then sends the message to the
                                                                        PHY to forward to the slave. The NPU stores the unique ID for later reference.
- message | Slave PHY    | Master PHY        | Delay Request Message  | The slave receives the Delay Request message from the NPU. It sees the
                                                                        extract field set in the 32 bit reserved field so it extracts both the
                                                                        unique ID and the current timewheel value and pushes them to its Egress
                                                                        Timestamp FIFO. This is the T3 timestamp value.
- message | Master PHY   | Master NPU        | Delay Request Message  | The Master receives the Delay Request message and stores the
                                                                        32 bit arrival timestamp (T4) in the 32 bit reserved field of the message
                                                                        header.
- action  | Master NPU   |                   | Record T4              | The Master NPU receives the Delay Request message from the PHY
                                                                        and extracts the 32 bit timestamp (T4) from the reserved field of the message
                                                                        header. It uses this information to construct the Delay_Resp message.
- message | Master NPU   | Master PHY        | Delay Response Message | The master constructs the Delay_Resp message and sets the receiveTimestamp
                                                                        to the T4 value recorded when it received the Delay Request message. It
                                                                        sets the extract field bit to zero so that the h/w does not capture the
                                                                        egress timestamp and sends the message to the PHY for forwarding to the
                                                                        slave.
- message | Master PHY   | Slave PHY         | Delay Response Message | The Master PHY forwards the message to the slave. The extraction
                                                                        bit is not set so it does not capture the timestamp from the message.
- message | Slave PHY    | Slave NPU         | Delay Response Message | The Slave NPU receives the Delay Response message from the Master and
                                                                        extracts the T4 timestamp from the receiveTimestamp field. It PTP session
                                                                        information to lookup the other timestamps for the session.
- action  | Slave NPU    |                   | Adjust Timewheel       | The Slave NPU calculates its offset from the master using T1, T2, T3, and T4
                                                                        and adjusts its timewheel to match. Depending on the difference the slave
                                                                        may choose to set the timewheel directly or it may adjust for minor drifts
                                                                        by using the UPDATE_COUNT register.

@sequence: title="Single Step Master" caption="Single Step Master Behavior"
- Type    | Source       | Sink              | Name                   | Description

# Two-Step Sync Message
- message | Master NPU   | Master PHY        | Sync Message           | The master NPU constructs a Sync Message to send to
                                                                        any slaves. It sets the twoStepFlag in the
                                                                        flagField field of the PTP header to indicate that this is a two
                                                                        step message and sets the originTimestamp and
                                                                        correctionFields to zero. It then generates a unique ID that
                                                                        uniquely identifies the PTP session
                                                                        and writes it to the 32 bit reserved field in the header
                                                                        and sets the extraction flag.
                                                                        This unique ID
                                                                        is used by the h/w to cache the departure timestamp (T1).
                                                                        The master then sends the Sync Message via the egress path of the h/w.
