
@h2 Sequence Diagrams
Shorte allows for automatic generation of sequence diagrams using the @sequence
tag. The syntax is similar to creating a table. This section describes some
examples of creating sequence diagrams.

@h3 @sequence
This tag is used to generate a sequence diagram.

@shorte
\@sequence: title="Sequence Diagram Title" caption="Sequence diagram caption"
- Type    | Source   | Sink         | Name                   | Description

- message | Master   | Slave        | Sync Message           | A sync message sent from master to slave.
- message | Slave    | Master       | Sync Response          | A response message from the slave.
- action  | Slave    |              | Random Event           | A random event on the slave.

@text
The above code generates a sequence diagram that looks something like this:

@sequence: title="Sequence Diagram Title" caption="Sequence diagram caption"
- Type    | Source   | Sink         | Name                   | Description

- message | Master   | Slave        | Sync Message           | A sync message sent from master to slave.
- message | Slave    | Master       | Sync Response          | A response message from the slave.
- action  | Slave    |              | Random Event           | A random event on the slave.
