#ifndef SETTINGSMANAGER_H
#define SETTINGSMANAGER_H

#include <QObject>
#include <QMap>
#include <QMultiMap>
#include <QStringList>
#include <QString>


class SettingsManager : public QObject
{
public:
    SettingsManager();

    bool load(const QString& path="settings.db");
    bool save(const QString& path="settings.db");

    void run_script(const QString& path);

    int find_dev(int msb, int lsb);

    void set(const QString& key, const QString& value);
    QString get(const QString& key);

    void set_dev(int device, const QString& key, const QString& value);
    QString get_dev(int device, const QString& key);

    void get_devices(QMap<int, QString>& devices);

    bool get_favorites(const QString& group, const QString& id, QMap<QString, QStringList>& favorites);
    bool set_favorites(const QString& group, const QString& id, QMap<QString, QStringList>& favorites);

    void get_globals(QMap<QString,QString>& glbs);
    void get_device_settings(int device, QMap<QString,QString>& settings);

    bool get_favorite_lists(
        int device,
        const QString& category,
        QStringList& favorites);

    bool get_favorite_list(
        int device,
        const QString& category,
        const QString& list,
        QStringList& favorites);

    void favorites_add_items(
        int device,
        const QString& category,
        const QString& list,
        QStringList& favorites);
    bool favorites_add_item(
        int device,
        const QString& category,
        const QString& list,
        const QString& favorite);
    bool favorites_move_item(
        int device,
        const QString& category,
        const QString& list,
        const QString& favorite,
        int            position);

    void favorites_remove_items(
        int device,
        const QString& category,
        const QString& list,
        QStringList& favorites);
    bool favorites_remove_item(
        int device,
        const QString& category,
        const QString& list,
        const QString& favorite);

    /**
     * This method is called to rename an item in a
     * favorites list.
     *
     * @param device    [I] - The device the list belongs to.
     * @param category  [I] - The group the list belongs to.
     * @param list      [I] - The name of the list.
     * @param curr_name [I] - The current name of the item.
     * @param new_name  [I] - The new name of the item.
     *
     * @return true on success, false on failure.
     */
    bool favorites_rename_item(
        int device,
        const QString& category,
        const QString& list,
        const QString& curr_name,
        const QString& new_name);

    bool were_settings_modified();

private:
    QMap<int,QString> m_device_list;
    QMap<QString, QString> m_globals;
    QMap<QString, QMap<QString, QStringList> > m_favorite_stats;
    QMap<QString, QMap<QString, QStringList> > m_favorite_regs;
    QMap<QString, QMap<QString, QString> >     m_device_info;

    QMap<int, QMap<QString,QString> > m_device_settings;

    /**
     * The list of favorites keyed by:
     *    chip -> category -> list -> items
     * where category are things like registers, stats, etc.
     */
    //QMap<int, QMap<QString, QMultiMap<QString,QString> > > m_favorites;
    QMap<int, QMap<QString, QMap<QString,QStringList> > > m_favorites;

    bool m_settings_modified;

};

#endif // SETTINGSMANAGER_H
