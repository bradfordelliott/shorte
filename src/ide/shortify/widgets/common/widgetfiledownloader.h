#ifndef WIDGETFILEDOWNLOADER_H
#define WIDGETFILEDOWNLOADER_H
#include <QObject>
#include <QUrl>
#include <QByteArray>
#include <QNetworkReply>
#include <QNetworkAccessManager>
#include <QString>

class WidgetFileDownloader : public QObject
{
    Q_OBJECT
public:
    explicit WidgetFileDownloader(QUrl url, QObject *parent = 0);

    virtual ~WidgetFileDownloader();

    QByteArray downloadedData() const;

    bool is_finished();
    bool is_errored();
    QString get_error();

private slots:

    void fileDownloaded(QNetworkReply* pReply);

private:

    QNetworkAccessManager m_WebCtrl;
    QByteArray m_DownloadedData;
    bool m_is_finished;

    QString m_error_string;
    bool m_is_errored;
};

#endif // WIDGETFILEDOWNLOADER_H
