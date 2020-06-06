# Sigchain

## Entry

| field | type          | notes                                             |
| ---   | ---           | ---                                               |
| sig   | Hex String    | Signature of Entry                                |
| data  | Base64 String | msppack encode of 'a statement'                   |
| kid   | Hex String    | Key used to sign Entry                            |
| prev  | Hex String    | SHA-256 hash of previous Entry - 0 if first entry |
| seq   | int           | sequence number in chain                          |
| time  | int           | unixtime-millis - not validated                   |

## Statements

### Create Device Key




