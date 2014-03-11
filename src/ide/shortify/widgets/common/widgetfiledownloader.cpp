#include <QUrl>
#include <QObject>
#include <QNetworkReply>
#include <QByteArray>


#include "widgets/common/widgetfiledownloader.h"


WidgetFileDownloader::WidgetFileDownloader(QUrl url, QObject* parent) : QObject(parent)
{
    m_is_finished = false;
    m_is_errored = false;

    connect(&m_WebCtrl, SIGNAL(finished(QNetworkReply*)),
        SLOT(fileDownloaded(QNetworkReply*)));

    QNetworkRequest request(url);
    m_WebCtrl.get(request);
}

WidgetFileDownloader::~WidgetFileDownloader()
{
}

QByteArray WidgetFileDownloader::downloadedData() const
{
    return m_DownloadedData;
}

bool WidgetFileDownloader::is_finished()
{
    return m_is_finished;
}

void WidgetFileDownloader::fileDownloaded(QNetworkReply* pReply)
{
    m_DownloadedData = pReply->readAll();

    if(QNetworkReply::NoError != pReply->error())
    {
        this->m_error_string = pReply->errorString();
        this->m_is_errored = true;
    }
    else
    {
        this->m_is_errored = false;
        this->m_error_string.clear();
    }

    pReply->close();
    pReply->deleteLater();

    m_is_finished = true;
}

bool WidgetFileDownloader::is_errored()
{
    return this->m_is_errored;
}


QString WidgetFileDownloader::get_error()
{
    return this->m_error_string;
}
