#include <QtTest/QtTest>

#include <QWebEngineView>
#include <QEventLoop>
#include <QTimer>

#include "UMarkdownViewerWidget.h"

class MarkdownMermaidTest : public QObject
{
    Q_OBJECT

private slots:
    void mermaidRendersSimpleDiagram();
};

void MarkdownMermaidTest::mermaidRendersSimpleDiagram()
{
#ifdef RDK_USE_QT_WEBENGINE
    // Готовим markdown с одной простой диаграммой
    const QString markdown = QString::fromUtf8(
        "```mermaid\n"
        "flowchart TD\n"
        "  A[Start] --> B[End]\n"
        "```"
    );

    // Используем тот же HTML‑пайплайн, что и в приложении
    UMarkdownViewerWidget widget;
    const QString html = widget.createHtmlFromMarkdown(markdown);

    QWebEngineView view;
    QSignalSpy loadSpy(&view, &QWebEngineView::loadFinished);

    view.setHtml(html, QUrl(QStringLiteral("qrc:/markdown/")));

    // Ждём завершения загрузки страницы
    QVERIFY2(loadSpy.wait(15000), "QWebEngineView::loadFinished не был получен в течение 15 секунд");
    QVERIFY2(loadSpy.takeFirst().at(0).toBool(), "Страница с markdown/mermaid не загрузилась успешно");

    // После загрузки проверяем, что mermaid отрисовал SVG внутри .mermaid
    QEventLoop loop;
    bool ok = false;

    view.page()->runJavaScript(
        "(function(){"
        "  var el = document.querySelector('#content .mermaid');"
        "  if (!el) return 'NO_MERMAID';"
        "  var svg = el.querySelector('svg');"
        "  return svg ? 'OK' : 'NO_SVG';"
        "})();",
        [&](const QVariant &result) {
            ok = (result.toString() == QLatin1String("OK"));
            loop.quit();
        }
    );

    QTimer::singleShot(15000, &loop, &QEventLoop::quit);
    loop.exec();

    QVERIFY2(ok, "Mermaid SVG не был найден внутри блока .mermaid");
#else
    QSKIP("RDK_USE_QT_WEBENGINE не активен, тест mermaid пропущен");
#endif
}

QTEST_MAIN(MarkdownMermaidTest)
#include "MarkdownMermaidTest.moc"

