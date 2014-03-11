#include "settingsmanager.h"
#include <QXmlStreamReader>
#include <QString>
#include <QXmlStreamWriter>
#include <QStringList>
#include <QTextStream>
#include <QFile>
#include <QMessageBox>
#include <QDebug>
#include <QDir>
#include <QTime>
#include <QVector>

#include "sqlite3.h"

class sqllite_col_t
{
public:
    QString name;
    QString value;
    int    type;
};

class sqllite_resultset_t
{
public:
    QVector<QVector<sqllite_col_t> > rows;
};


//+-------------------------------------------------------------------------------
//|
//| NAME:
//|    sqlite_callback()
//|
//| PARAMETERS:
//|    data      (I) - The output data structure where query data returned from
//|                    the SQLite database will be written.
//|    argc      (I) - The number of rows returned from the database.
//|    argv      (I) - The actual contents of the rows returned from the database.
//|    azColName (I) - The list of column names returned from the database.
//|
//| DESCRIPTION:
//|    This is a callback method used by the query function to parse the results
//|    of the query and store them in a resultset object.
//|
//| RETURNS:
//|    0 for now because this is what sqlite3_exec() requires.
//|
//+-------------------------------------------------------------------------------
int sqlite_callback(void* data, int argc, char **argv, char **azColName)
{
    int i;
    sqllite_resultset_t* rs = (sqllite_resultset_t*)data;
    //QVector<sqllite_col_t> cols(argc);
    sqllite_col_t col;
    QVector<sqllite_col_t> cols(10);

    for(i=0; i<argc; i++)
    {
        col.value = argv[i] ? argv[i] : "NULL";
        col.name  = azColName[i] ? azColName[i] : "NULL";
        cols[i] = col;
    }
    rs->rows.append(cols);

    return 0;
}

QString add_slashes(const QString& input)
{
    QString output = input;
    output = output.replace("'", "''");

    return output;
}

QString strip_slashes(const QString& input)
{
    QString output = input;
    output = output.replace("''", "'");
    output = output.replace("&apos;", "'");

    return output;
}


SettingsManager::SettingsManager()
{
    m_settings_modified = false;
}

sqlite3* m_db;

bool SettingsManager::load(const QString& path)
{
    QByteArray data = path.toLatin1();

    if(sqlite3_open(data.constData(), &(m_db)))
    {
        sqlite3_close(m_db);
        return false;
    }

#if defined(SQLITE_HAS_CODEC)
    char tmp[9];
    // Grab the obfuscated key
    sqlite3_obfuscate_key(tmp);
    tmp[8] = 0;

    if(SQLITE_OK != sqlite3_key((sqlite3*) m_db, tmp, 8))
    {
        memset(tmp, 0, 9);
        sqlite3_close(m_db);
        return false;
    }
    // Clear the key so it isn't stored in memory
    memset(tmp, 0, 9);
#endif

    sqllite_resultset_t rs;
    int rc;

    const char* query = "SELECT key,value FROM Settings";
    rc = sqlite3_exec((sqlite3*)m_db, query, sqlite_callback, &rs, NULL);
    for(int i = 0; i < rs.rows.size(); i++)
    {
        QString key = strip_slashes(rs.rows[i][0].value);
        QString value = strip_slashes(rs.rows[i][1].value);
        m_globals[key] = strip_slashes(value);
    }

    bool allow_protected_settings = false;
    if(m_globals.end() != m_globals.find("permissions.protected_settings_visible"))
    {
        QString val = m_globals["permissions.protected_settings_visible"];
        if(val == "1")
        {
            allow_protected_settings = true;
        }
    }

    query = "SELECT chip,key,value FROM DeviceSettings";
    rs.rows.clear();
    rc = sqlite3_exec((sqlite3*)m_db, query, sqlite_callback, &rs, NULL);
    for(int i = 0; i < rs.rows.size(); i++)
    {
        QString chip  = strip_slashes(rs.rows[i][0].value);
        QString key   = strip_slashes(rs.rows[i][1].value);
        QString value = strip_slashes(rs.rows[i][2].value);

        int chip_id = chip.toInt(0,10);
        m_device_settings[chip_id][key] = value;
    }

    query = "SELECT chip,key,value FROM DeviceSettings WHERE key='name'";
    rs.rows.clear();
    rc = sqlite3_exec((sqlite3*)m_db, query, sqlite_callback, &rs, NULL);
    for(int i = 0; i < rs.rows.size(); i++)
    {
        QString chip = strip_slashes(rs.rows[i][0].value);
        QString key = strip_slashes(rs.rows[i][1].value);
        QString value = strip_slashes(rs.rows[i][2].value);
        int chip_id = chip.toInt(0,10);

        /* Ensure the driver exists before adding this chip */
        if(m_device_settings[chip_id].contains("scripts.c.path"))
        {
            QString driver_path = m_device_settings[chip_id]["scripts.c.path"];

            if(QDir(driver_path).exists())
            {
                m_device_list[chip_id] = value;
            }
        }
    }

    if(allow_protected_settings)
    {
        query = "SELECT chip,category,key,value FROM DeviceLists";
    }
    else
    {
        query = "SELECT chip,category,key,value FROM DeviceLists WHERE protected='0'";
    }

    rs.rows.clear();
    rc = sqlite3_exec((sqlite3*)m_db, query, sqlite_callback, &rs, NULL);
    for(int i = 0;i < rs.rows.size(); i++)
    {
        int chip = rs.rows[i][0].value.toInt();
        QString category = strip_slashes(rs.rows[i][1].value);
        QString list = strip_slashes(rs.rows[i][2].value);
        QString entry = strip_slashes(rs.rows[i][3].value);

        //qDebug() << "Loading " << chip << "." << category << "." << list << "." << entry << "\n";
        //m_favorites[chip][category].insert(list,entry);
        m_favorites[chip][category][list].append(entry);
    }

    sqlite3_close(m_db);

    return true;
}

#include <QFile>
#include <QTextStream>

void SettingsManager::run_script(const QString& path)
{
    QString query;
    QFile script(path);
    if(!script.open(QIODevice::ReadOnly))
    {
        QMessageBox::warning(NULL, "File Open Failure",
            QString("Failed opening %1").arg(path));
        return;
    }

    QTextStream input(&script);
    QString contents = input.readAll();
    QTextStream::Status status = input.status();
    if(status != QTextStream::Ok)
    {
        QMessageBox::warning(NULL, "Failed Loading Script File",
            QString("Failed loading %1").arg(path));
        return;
    }

    QByteArray data = contents.toLatin1();
    sqlite3_exec((sqlite3*)m_db, data.constData(), NULL, NULL, NULL);
}

bool SettingsManager::save(const QString& path)
{
    QByteArray data = path.toLatin1();

    if(sqlite3_open(data.constData(), &(m_db)))
    {
        sqlite3_close(m_db);
        return false;
    }

#if defined(SQLITE_HAS_CODEC)
    char tmp[9];
    // Grab the obfuscated key
    sqlite3_obfuscate_key(tmp);

    if(SQLITE_OK != sqlite3_key((sqlite3*) m_db, tmp, 8))
    {
        memset(tmp, 0, 9);
        sqlite3_close(m_db);
        return false;
    }
    // Clear the key so it isn't stored in memory
    memset(tmp, 0, 9);
#endif


    QMap<QString, QString>::iterator siter;
    QString query = "BEGIN TRANSACTION;\n";

    sqllite_resultset_t rs;
    int rc;

    for(siter = m_globals.begin(); siter != m_globals.end(); siter++)
    {
        QString k = siter.key();
        QString v = siter.value();

        query += QString("UPDATE Settings SET value='%1' WHERE key='%2';\n").
            arg(add_slashes(v)).
            arg(add_slashes(k));

    }



    QMap<int, QMap<QString, QMap<QString,QStringList> > >::iterator fiter;

    query += QString("DELETE FROM DeviceLists;\n");
    //rs.rows.clear();
    //sqlite3_exec((sqlite3*)m_db, qPrintable(query), NULL, NULL, NULL);

    for(fiter = m_favorites.begin();
        fiter != m_favorites.end();
        fiter++)
    {
        QMap<QString, QMap<QString,QStringList> >::iterator liter;

        int chip = fiter.key();

        for(liter = fiter.value().begin();
            liter != fiter.value().end();
            liter++)
        {
            QString category = liter.key();
            QMap<QString,QStringList> lists = liter.value();
            QMap<QString,QStringList>::iterator viter;

            for(viter = lists.begin(); viter != lists.end(); viter++)
            {
                QString list = viter.key();
                QStringList items = viter.value();

                for(int i = 0; i < items.count(); i++)
                {
                    QString item = items.at(i);

                    query += QString("INSERT INTO DeviceLists (chip,category,key,value) VALUES('%1', '%2', '%3', '%4');\n").
                            arg(chip).
                            arg(add_slashes(category)).
                            arg(add_slashes(list)).
                            arg(add_slashes(item));
                    //qDebug() << query;

                    //sqlite3_exec((sqlite3*)m_db, qPrintable(query), NULL, NULL, NULL);
                }
            }
        }
    }

    query += "END TRANSACTION;\n";

    data = query.toLatin1();
    rc = sqlite3_exec((sqlite3*)m_db, data.constData(), NULL, NULL, NULL);

    sqlite3_close(m_db);

    if(rc == SQLITE_OK)
    {
        // Settings no longer modified after writing back to dB
        m_settings_modified = false;
        return true;
    }

    return false;
}


QString SettingsManager::get(const QString& key)
{
    QStringList parts = key.split("/");
    QString group = parts.at(0);
    QString k;

    if(parts.length() > 1)
    {
        k = parts.at(1);
    }
    else
    {
        group = "global";
        k = parts.at(0);
    }

    if(group == "global")
    {
        return m_globals[k];
    }
    else if(group == "device")
    {
        return m_device_info[k][parts.at(2)];
    }

    return "";
}

void SettingsManager::set(const QString& key, const QString& value)
{
    QStringList parts = key.split("/");
    QString group = parts.at(0);
    QString k;

    m_settings_modified = true;

    if(parts.length() > 1)
    {
        k = parts.at(1);
    }
    else
    {
        group = "global";
        k = parts.at(0);
    }

    if(group == "global")
    {
        m_globals[k] = value;
    }
    else if(group == "device")
    {
        m_device_info[k][parts.at(2)] = value;
    }
}

void SettingsManager::set_dev(int device, const QString& key, const QString& value)
{
    m_device_settings[device][key] = value;
    m_settings_modified = true;
}

QString SettingsManager::get_dev(int device, const QString& key)
{
    // First search for a match on the device
    if(m_device_settings[device].end() == m_device_settings[device].find(key))
    {
        // If that is not found try a mask (-1)
        if(m_device_settings[-1].end() != m_device_settings[-1].find(key))
        {
            return m_device_settings[-1][key];
        }
    }

    return m_device_settings[device][key];
}


bool SettingsManager::get_favorites(const QString& group, const QString& id, QMap<QString, QStringList>& favorites)
{
    if(group == "stats")
    {
        favorites = m_favorite_stats[id];
    }

    return true;
}

bool SettingsManager::get_favorite_lists(
    int device,
    const QString& category,
    QStringList& favorites)
{
    QSet<QString> items = QSet<QString>::fromList(m_favorites[device][category].keys());

    if(!items.contains("Recent"))
    {
        items.insert("Recent");
    }

    favorites = items.toList();

    //for(int i = 0; i < favorites.length(); i++)
    //{
    //    qDebug() << "list: " << favorites.at(i);
    //}
    //favorites.sort();
    return true;
}

bool SettingsManager::get_favorite_list(
    int device,
    const QString& category,
    const QString& list,
    QStringList& favorites)
{
    favorites = m_favorites[device][category][list];

    //favorites.sort();

    return true;
}

void SettingsManager::favorites_add_items(
    int device,
    const QString& category,
    const QString& list,
    QStringList& favorites)
{
    for(int i = 0; i < favorites.length(); i++)
    {
        /*if(!m_favorites[device][category].contains(list,favorites.at(i)))
        {
            m_favorites[device][category].insert(list,favorites.at(i));
        }
        */
        if(!m_favorites[device][category][list].contains(favorites.at(i)))
        {
            m_favorites[device][category][list].append(favorites.at(i));
        }

    }
    m_settings_modified = true;
}
bool SettingsManager::favorites_add_item(
    int device,
    const QString& category,
    const QString& list,
    const QString& favorite)
{
/*
    if(!m_favorites[device][category].contains(list,favorite))
    {
        //qDebug() << "Adding " << category << "." << favorite << "." << list << " for device " << device;
        m_favorites[device][category].insert(list,favorite);

        if(!m_favorites[device][category].contains(list,favorite))
        {
            //qDebug() << "Failed adding " << favorite;
        }
    }
*/
    if(!m_favorites[device][category][list].contains(favorite))
    {
        //qDebug() << "Adding " << category << "." << favorite << "." << list << " for device " << device;
        m_favorites[device][category][list].append(favorite);
    }

    m_settings_modified = true;

    return true;
}

bool SettingsManager::favorites_move_item(
        int device,
        const QString& category,
        const QString& list,
        const QString& favorite,
        int            offset)
{
    int index = m_favorites[device][category][list].indexOf(favorite);
    int count = m_favorites[device][category][list].count();

    //m_favorites[device][category][list].removeAt(index);

    if(offset == 2)
    {
        offset = m_favorites[device][category][list].count() - 1;
    }
    else if(offset == -2)
    {
        offset = 0;
    }
    // If we're at the start of the list and a request to move backwards
    // was found then go to the end of the list
    else if(index == 0 && offset == -1)
    {
        offset = m_favorites[device][category][list].count() - 1;
    }
    else if(index == (count-1) && offset == 1)
    {
        offset = 0;
    }
    else
    {
        offset = index + offset;
    }

    m_favorites[device][category][list].move(index, offset);

    m_settings_modified = true;

    return true;
}

void SettingsManager::favorites_remove_items(
    int device,
    const QString& category,
    const QString& list,
    QStringList& favorites)
{
    for(int i = 0; i < favorites.length(); i++)
    {
        m_favorites[device][category][list].removeAll(favorites.at(i));
        //m_favorites[device][category].remove(list,favorites.at(i));
    }

    m_settings_modified = true;
}
bool SettingsManager::favorites_remove_item(
    int device,
    const QString& category,
    const QString& list,
    const QString& favorite)
{
    //qDebug() << "Removing " << list << "." << favorite;
    m_favorites[device][category][list].removeAll(favorite);

    //m_favorites[device][category].remove(list,favorite);

    m_settings_modified = true;

    return true;
}

bool SettingsManager::favorites_rename_item(
        int device,
        const QString& category,
        const QString& list,
        const QString& curr_name,
        const QString& new_name)
{
    for(int i = 0; i < m_favorites[device][category][list].count(); i++)
    {
        if(m_favorites[device][category][list].at(i) == curr_name)
        {
            m_favorites[device][category][list][i] = new_name;
        }
    }

    m_settings_modified = true;

    return true;
}



bool SettingsManager::set_favorites(const QString& group, const QString& id, QMap<QString, QStringList>& favorites)
{
    if(group == "stats")
    {
        m_favorite_stats[id] = favorites;
    }

    m_settings_modified = true;

    return true;
}


void SettingsManager::get_devices(QMap<int, QString>& devices)
{
    devices = this->m_device_list;
}


int SettingsManager::find_dev(int msb, int lsb)
{
    QString expected_id;
    expected_id.sprintf("%04x_%04x", msb, lsb);

    QMap<int, QMap<QString,QString> >::iterator iter;

    for(iter = m_device_settings.begin();
        iter != m_device_settings.end();
        iter++)
    {
        int id = iter.key();

        QRegExp expr(iter.value()["chip.id"]);

        if(expr.exactMatch(expected_id))
        {
            return id;
        }
    }

    return -1;
}


void SettingsManager::get_globals(QMap<QString, QString>& glbs)
{
    glbs = this->m_globals;
}


void SettingsManager::get_device_settings(int device, QMap<QString,QString>& settings)
{
    settings = this->m_device_settings[device];
}

bool SettingsManager::were_settings_modified()
{
    return m_settings_modified;
}
