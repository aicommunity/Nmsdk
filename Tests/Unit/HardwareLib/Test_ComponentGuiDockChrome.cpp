#include <gtest/gtest.h>

#include <QApplication>
#include <QDockWidget>
#include <QMainWindow>

#include "../../../Rdk/GUI/Qt/UComponentGuiDockChrome.h"

namespace {
void EnsureApp()
{
    static int argc = 1;
    static char arg0[] = "test";
    static char* argv[] = {arg0, nullptr};
    if (!qApp)
        new QApplication(argc, argv);
}
}

TEST(ComponentGuiDockChrome, FloatingHasMinMaxWithoutCustomizeHint)
{
    EnsureApp();
    QMainWindow mw;
    auto* dock = new QDockWidget(QStringLiteral("t"), &mw);
    mw.addDockWidget(Qt::RightDockWidgetArea, dock);
    installComponentGuiFloatingChrome(dock);
    dock->show();
    mw.show();
    dock->setFloating(true);
    QApplication::sendPostedEvents();
    QApplication::processEvents();
    EXPECT_TRUE(dock->windowFlags() & Qt::WindowMinimizeButtonHint);
    EXPECT_TRUE(dock->windowFlags() & Qt::WindowMaximizeButtonHint);
    EXPECT_FALSE(dock->windowFlags() & Qt::CustomizeWindowHint);
    dock->showMaximized();
    QApplication::processEvents();
    EXPECT_TRUE(dock->isMaximized());
    EXPECT_TRUE(dock->isFloating());
}
