@doctitle Sequences
@doctitle Sequence Diagram Tests

@body
@h1 Sequence Diagram

@sequence: title="Hitachi KR"
- Type    | Source         | Sink           | Name                           | Description
- action  | API            |                | Initialization                 | The API starts initializing the ASIC, the microsequencer is currently stalled 
- message | API            | Microsequencer | SPARE1[0] == 1, SPARE1[4] == 1 | The API starts AN by setting SPARE1[0] == 1.
- loop    | API            |                | Wait for SPARE20 == 1          | The API waits for AN completion by polling for SPARE20 == 1
- message | Microsequencer | KR             | Enable AN                      | The microsequencer triggers the AN block to start sending DME pages to the
                                                                               link partner.
- message | KR             | Link Partner   | DME pages                      | The link partner exchanges DME pages while negotation is performed
- message | Link Partner   | KR             | DME pages                      |
- message | KR             | Link Partner   | Training                       | Taps are trained
- message | Link Partner   | KR             | Training                       | Taps are trained
- message | KR             | Microsequencer | AN Complete                    |
- message | Microsequencer | API            | SPARE20 = 1                    | The microsequencer asserts SPARE20
- action  | API            |                | Configure host                 | The API finishes by configuring the host interface based on the negotiated results.


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

