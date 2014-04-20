#ifndef DIALOGSETTINGSMANAGER_H
#define DIALOGSETTINGSMANAGER_H

#include <QDialog>
#include <QMap>
#include <QString>

namespace Ui {
class DialogSettingsManager;
}

class DialogSettingsManager : public QDialog
{
    Q_OBJECT
    
public:
    explicit DialogSettingsManager(QWidget *parent = 0);
    ~DialogSettingsManager();

    bool set_keys(const QString& group, QMap<QString,QString>& keys);
    void set_database(class SettingsManager* db);
    
private slots:
    void on_button_cancel_clicked();

    void on_button_save_clicked();

private:
    Ui::DialogSettingsManager *ui;

    QMap<QString, QMap<QString,QString> > m_keys;
    class SettingsManager* m_db;
};

#endif // DIALOGSETTINGSMANAGER_H
