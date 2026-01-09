#include <QApplication>
#include <QMainWindow>
#include <QPushButton>
#include <QVBoxLayout>
#include <QWidget>
#include <QMessageBox>
#include <QLabel>
#include <QDebug>

class TestWindow : public QMainWindow
{
    Q_OBJECT

public:
    TestWindow(QWidget *parent = nullptr) : QMainWindow(parent)
    {
        setWindowTitle("QMessageBox Production Test - Using Bin/Platform/Win Qt");
        setMinimumSize(500, 400);
        
        QWidget *centralWidget = new QWidget(this);
        setCentralWidget(centralWidget);
        
        QVBoxLayout *layout = new QVBoxLayout(centralWidget);
        
        infoLabel = new QLabel("Production Test: Используются Qt DLL и плагины из Bin/Platform/Win", this);
        infoLabel->setWordWrap(true);
        infoLabel->setStyleSheet("QLabel { background-color: #e3f2fd; padding: 10px; border: 1px solid #2196F3; }");
        layout->addWidget(infoLabel);
        
        // Тест 1: Точное воспроизведение кода из строки 483 UGEngineControlWidget.cpp
        QPushButton *test1Button = new QPushButton("Test 1: Exact code from line 483 (FIXED)", this);
        connect(test1Button, &QPushButton::clicked, this, &TestWindow::test1);
        layout->addWidget(test1Button);
        
        // Тест 2: Прямое сравнение (старый проблемный способ)
        QPushButton *test2Button = new QPushButton("Test 2: Direct comparison (OLD WAY - may crash)", this);
        connect(test2Button, &QPushButton::clicked, this, &TestWindow::test2);
        layout->addWidget(test2Button);
        
        // Тест 3: Множественные вызовы для проверки стабильности
        QPushButton *test3Button = new QPushButton("Test 3: Multiple calls (stress test)", this);
        connect(test3Button, &QPushButton::clicked, this, &TestWindow::test3);
        layout->addWidget(test3Button);
        
        resultLabel = new QLabel("Результат: Ожидание...", this);
        resultLabel->setWordWrap(true);
        resultLabel->setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc; min-height: 60px; }");
        layout->addWidget(resultLabel);
        
        layout->addStretch();
    }

private slots:
    void test1()
    {
        infoLabel->setText("Test 1: Точное воспроизведение кода из строки 483 UGEngineControlWidget.cpp (ИСПРАВЛЕННЫЙ СПОСОБ)");
        resultLabel->setText("Результат: Выполняется...");
        QApplication::processEvents();
        
        try {
            // ТОЧНОЕ ВОСПРОИЗВЕДЕНИЕ КОДА ИЗ СТРОКИ 477-484 UGEngineControlWidget.cpp
            // Убеждаемся, что виджет видим и активен перед показом диалога (важно для Windows)
            if (!isVisible() || !isActiveWindow()) {
                raise();
                activateWindow();
            }
            
            QMessageBox::StandardButton reply = QMessageBox::question(this, "Info", "Close current config?", QMessageBox::Yes|QMessageBox::No);
            if (reply != QMessageBox::Yes)
            {
                resultLabel->setText("✅ Результат Test 1: УСПЕХ - Выбран No (код работает корректно)");
                resultLabel->setStyleSheet("QLabel { background-color: #d4edda; padding: 10px; border: 1px solid #c3e6cb; min-height: 60px; }");
                return;
            }
            
            resultLabel->setText("✅ Результат Test 1: УСПЕХ - Выбран Yes (код работает корректно)");
            resultLabel->setStyleSheet("QLabel { background-color: #d4edda; padding: 10px; border: 1px solid #c3e6cb; min-height: 60px; }");
        } catch (...) {
            resultLabel->setText("❌ Результат Test 1: ОШИБКА - Исключение!");
            resultLabel->setStyleSheet("QLabel { background-color: #f8d7da; padding: 10px; border: 1px solid #f5c6cb; min-height: 60px; }");
        }
    }
    
    void test2()
    {
        infoLabel->setText("Test 2: Прямое сравнение (СТАРЫЙ ПРОБЛЕМНЫЙ СПОСОБ - как было до исправления)");
        resultLabel->setText("Результат: Выполняется...");
        QApplication::processEvents();
        
        try {
            // Убеждаемся, что виджет видим и активен
            if (!isVisible() || !isActiveWindow()) {
                raise();
                activateWindow();
            }
            
            // Проблемный способ - прямое сравнение (как было в оригинальном коде на строке 477)
            if (QMessageBox::question(this, "Info", "Close current config?", QMessageBox::Yes|QMessageBox::No) != QMessageBox::Yes) {
                resultLabel->setText("✅ Результат Test 2: УСПЕХ - Выбран No (прямое сравнение работает)");
                resultLabel->setStyleSheet("QLabel { background-color: #d4edda; padding: 10px; border: 1px solid #c3e6cb; min-height: 60px; }");
            } else {
                resultLabel->setText("✅ Результат Test 2: УСПЕХ - Выбран Yes (прямое сравнение работает)");
                resultLabel->setStyleSheet("QLabel { background-color: #d4edda; padding: 10px; border: 1px solid #c3e6cb; min-height: 60px; }");
            }
        } catch (...) {
            resultLabel->setText("❌ Результат Test 2: ОШИБКА - Исключение при прямом сравнении!");
            resultLabel->setStyleSheet("QLabel { background-color: #f8d7da; padding: 10px; border: 1px solid #f5c6cb; min-height: 60px; }");
        }
    }
    
    void test3()
    {
        infoLabel->setText("Test 3: Множественные последовательные вызовы (стресс-тест)");
        resultLabel->setText("Результат: Выполняется...");
        QApplication::processEvents();
        
        try {
            int successCount = 0;
            int failCount = 0;
            
            for (int i = 0; i < 5; i++) {
                if (!isVisible() || !isActiveWindow()) {
                    raise();
                    activateWindow();
                }
                
                // Используем исправленный способ
                QMessageBox::StandardButton reply = QMessageBox::question(
                    this, 
                    "Info", 
                    QString("Question %1 of 5. Close current config?").arg(i + 1), 
                    QMessageBox::Yes | QMessageBox::No
                );
                
                if (reply == QMessageBox::Yes || reply == QMessageBox::No) {
                    successCount++;
                } else {
                    failCount++;
                }
            }
            
            resultLabel->setText(QString("✅ Результат Test 3: УСПЕХ - Успешных: %1, Ошибок: %2").arg(successCount).arg(failCount));
            resultLabel->setStyleSheet("QLabel { background-color: #d4edda; padding: 10px; border: 1px solid #c3e6cb; min-height: 60px; }");
        } catch (...) {
            resultLabel->setText("❌ Результат Test 3: ОШИБКА - Исключение!");
            resultLabel->setStyleSheet("QLabel { background-color: #f8d7da; padding: 10px; border: 1px solid #f5c6cb; min-height: 60px; }");
        }
    }

private:
    QLabel *infoLabel;
    QLabel *resultLabel;
};

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    
    TestWindow window;
    window.show();
    
    return app.exec();
}

#include "Test_QMessageBox_Production.moc"
