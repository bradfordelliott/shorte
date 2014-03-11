#ifndef WIDGETSCRIPTLIBRARY_H
#define WIDGETSCRIPTLIBRARY_H

#include <QWidget>

namespace Ui {
    class WidgetScriptLibrary;
}

class WidgetScriptLibrary : public QWidget
{
    Q_OBJECT

public:
    explicit WidgetScriptLibrary(QWidget *parent = 0);
    ~WidgetScriptLibrary();

private:
    Ui::WidgetScriptLibrary *ui;
};

#endif // WIDGETSCRIPTLIBRARY_H
