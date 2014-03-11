#ifndef __GUI_TYPES_H__
#define __GUI_TYPES_H__
#include <QVariant>
#include <QEvent>

template <class T> class VPtr
{
public:
    static T* asPtr(QVariant v)
    {
        return  (T *) v.value<void *>();
    }

    static QVariant asQVariant(T* ptr)
    {
        return qVariantFromValue((void *) ptr);
    }
};

typedef enum
{
    CS_TARGET_LEEDS       = 0,
    CS_TARGET_LEEDSB      = 1,
    CS_TARGET_T100        = 2,
    CS_TARGET_VILLA3      = 3,
    CS_TARGET_K2          = 4,
    CS_TARGET_T41         = 5,
    CS_TARGET_OCTALVILLA3 = 6,
    CS_TARGET_MX00        = 7,
    CS_TARGET_K3          = 8,
    CS_TARGET_UNKNOWN = -1
}e_cs_chip_id;

typedef enum
{
    TARGET_NOT_CONNECTED                = 0,
    TARGET_CONNECT_VIA_USB_PROTOCOL     = 1,
    TARGET_CONNECT_VIA_SPY_PROTOCOL     = 2,
    TARGET_CONNECT_VIA_XMLRPC_PROTOCOL  = 3
}e_connect_method;

typedef enum
{
    CS_SCRIPT_TYPE_PYTHON = 1,
    CS_SCRIPT_TYPE_C      = 2,
    CS_SCRIPT_TYPE_PERL   = 3,
    CS_SCRIPT_TYPE_TEXT   = 4,
    CS_SCRIPT_TYPE_EEPROM = 5,
    CS_SCRIPT_TYPE_SHORTE = 6,
}e_cs_script_type;


typedef enum
{
    CS_ACTION_REGISTER_READ = 0,
    CS_ACTION_REGISTER_WRITE = 1,
    CS_ACTION_BITFIELD_WRITE = 2,
    CS_ACTION_STAT_READ      = 3,
    CS_ACTION_STATS_CLEAR    = 4
}e_cs_action_type;

#include <QEvent>

const int EventRegReadType = 1099;
const int EventRegWriteType = 1100;
const int EventRegBitfieldWriteType = 1101;
const int EventRecordDisable = 1102;
const int EventRecordEnable = 1103;
const int EventRecordRefreshDisable = 1104;
const int EventRecordRefreshEnable = 1105;
const int EventRegWriteArrayType = 1106;
const int EventRegReadArrayType = 1107;


class EventRegRead : public QEvent
{
public:
    EventRegRead(
        quint32 slice,
        quint32 address,
        quint64 data): QEvent((QEvent::Type)EventRegReadType)
    {
        m_slice = slice;
        m_address = address;
        m_data = data;
    }

    EventRegRead(const EventRegRead& rhs) : QEvent((QEvent::Type)EventRegReadType)
    {
        m_slice = rhs.m_slice;
        m_address = rhs.m_address;
        m_data = rhs.m_data;
    }

    ~EventRegRead()
    {
    }

    quint32 m_slice;
    quint32 m_address;
    quint64 m_data;
};

class EventRegWrite : public QEvent
{
public:
    EventRegWrite(
        quint32 slice,
        quint32 address,
        quint64 data): QEvent((QEvent::Type)EventRegWriteType)
    {
        m_slice = slice;
        m_address = address;
        m_data = data;
    }

    EventRegWrite(const EventRegWrite& rhs) : QEvent((QEvent::Type)EventRegWriteType)
    {
        m_slice = rhs.m_slice;
        m_address = rhs.m_address;
        m_data = rhs.m_data;
    }

    ~EventRegWrite()
    {
    }

    quint32 m_slice;
    quint32 m_address;
    quint64 m_data;
};

class EventRegWriteArray : public QEvent
{
public:
    EventRegWriteArray(
        quint32 slice,
        QVector<quint32>& address,
        QVector<quint64>& data): QEvent((QEvent::Type)EventRegWriteArrayType)
    {
        m_slice = slice;
        m_address = address;
        m_data = data;
    }

    EventRegWriteArray(const EventRegWriteArray& rhs) : QEvent((QEvent::Type)EventRegWriteArrayType)
    {
        m_slice = rhs.m_slice;
        m_address = rhs.m_address;
        m_data = rhs.m_data;
    }

    ~EventRegWriteArray()
    {
    }

    quint32 m_slice;
    QVector<quint32> m_address;
    QVector<quint64> m_data;
};

class EventRegReadArray : public QEvent
{
public:
    EventRegReadArray(
        quint32 slice,
        QVector<quint32>& address,
        QVector<quint64>& data): QEvent((QEvent::Type)EventRegReadArrayType)
    {
        m_slice = slice;
        m_address = address;
        m_data = data;
    }

    EventRegReadArray(const EventRegWriteArray& rhs) : QEvent((QEvent::Type)EventRegReadArrayType)
    {
        m_slice = rhs.m_slice;
        m_address = rhs.m_address;
        m_data = rhs.m_data;
    }

    ~EventRegReadArray()
    {
    }

    quint32 m_slice;
    QVector<quint32> m_address;
    QVector<quint64> m_data;
};

class EventRegBitfieldWrite : public QEvent
{
public:
    EventRegBitfieldWrite(
        quint32 slice,
        quint32 address,
        const QString& bitfield,
        quint64 data): QEvent((QEvent::Type)EventRegBitfieldWriteType)
    {
        m_slice = slice;
        m_address = address;
        m_data = data;
        m_bitfield = bitfield;
    }
    EventRegBitfieldWrite(const EventRegBitfieldWrite& rhs) : QEvent((QEvent::Type)EventRegBitfieldWriteType)
    {
        m_slice = rhs.m_slice;
        m_address = rhs.m_address;
        m_data = rhs.m_data;
        m_bitfield = rhs.m_bitfield;
    }

    ~EventRegBitfieldWrite()
    {
    }

    quint32 m_slice;
    quint32 m_address;
    quint64 m_data;
    QString m_bitfield;
};


#endif /* __GUI_TYPES_H__ */
