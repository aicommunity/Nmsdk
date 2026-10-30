// Standalone тест для быстрой проверки QMessageBox::question в Windows
// Компиляция: g++ -o Test_QMessageBox_Standalone.exe Test_QMessageBox_Standalone.cpp -I<Qt_include_path> -L<Qt_lib_path> -lQt5Core -lQt5Widgets -fPIC
// Или с Qt6: g++ -o Test_QMessageBox_Standalone.exe Test_QMessageBox_Standalone.cpp -I<Qt6_include_path> -L<Qt6_lib_path> -lQt6Core -lQt6Widgets -fPIC

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
        setWindowTitle("QMessageBox Test - Windows Standalone");
        setMinimumSize(500, 400);
        
        QWidget *centralWidget = new QWidget(this);
        setCentralWidget(centralWidget);
        
        QVBoxLayout *layout = new QVBoxLayout(centralWidget);
        
        infoLabel = new QLabel("Нажмите кнопку для тестирования QMessageBox::question", this);
        infoLabel->setWordWrap(true);
        layout->addWidget(infoLabel);
        
        // Тест 1: Правильный способ с сохранением в переменную (как исправлено в коде)
        QPushButton *test1Button = new QPushButton("Test 1: StandardButton reply = QMessageBox::question(...)", this);
        connect(test1Button, &QPushButton::clicked, this, &TestWindow::test1);
        layout->addWidget(test1Button);
        
        // Тест 2: Прямое сравнение (старый проблемный способ)
        QPushButton *test2Button = new QPushButton("Test 2: Direct comparison (OLD WAY - may crash)", this);
        connect(test2Button, &QPushButton::clicked, this, &TestWindow::test2);
        layout->addWidget(test2Button);
        
        // Тест 3: С проверкой видимости (как в исправленном коде)
        QPushButton *test3Button = new QPushButton("Test 3: With visibility check (FIXED WAY)", this);
        connect(test3Button, &QPushButton::clicked, this, &TestWindow::test3);
        layout->addWidget(test3Button);
        
        resultLabel = new QLabel("Результат: Ожидание...", this);
        resultLabel->setWordWrap(true);
        resultLabel->setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc; }");
        layout->addWidget(resultLabel);
        
        layout->addStretch();
    }

private slots:
    void test1()
    {
        infoLabel->setText("Test 1: Используется QMessageBox::StandardButton reply = QMessageBox::question(...)");
        resultLabel->setText("Результат: Выполняется...");
        QApplication::processEvents();
        
        try {
            // Убеждаемся, что виджет видим и активен
            if (!isVisible() || !isActiveWindow()) {
                raise();
                activateWindow();
            }
            
            QMessageBox::StandardButton reply = QMessageBox::question(
                this, 
                "Info", 
                "Close current config?", 
                QMessageBox::Yes | QMessageBox::No
            );
            
            if (reply == QMessageBox::Yes) {
                resultLabel->setText("✅ Результат Test 1: УСПЕХ - Выбран Yes");
                resultLabel->setStyleSheet("QLabel { background-color: #d4edda; padding: 10px; border: 1px solid #c3e6cb; }");
            } else {
                resultLabel->setText("✅ Результат Test 1: УСПЕХ - Выбран No");
                resultLabel->setStyleSheet("QLabel { background-color: #d4edda; padding: 10px; border: 1px solid #c3e6cb; }");
            }
        } catch (...) {
            resultLabel->setText("❌ Результат Test 1: ОШИБКА - Исключение!");
            resultLabel->setStyleSheet("QLabel { background-color: #f8d7da; padding: 10px; border: 1px solid #f5c6cb; }");
        }
    }
    
    void test2()
    {
        infoLabel->setText("Test 2: Используется прямое сравнение (СТАРЫЙ ПРОБЛЕМНЫЙ СПОСОБ)");
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
                resultLabel->setStyleSheet("QLabel { background-color: #d4edda; padding: 10px; border: 1px solid #c3e6cb; }");
            } else {
                resultLabel->setText("✅ Результат Test 2: УСПЕХ - Выбран Yes (прямое сравнение работает)");
                resultLabel->setStyleSheet("QLabel { background-color: #d4edda; padding: 10px; border: 1px solid #c3e6cb; }");
            }
        } catch (...) {
            resultLabel->setText("❌ Результат Test 2: ОШИБКА - Исключение при прямом сравнении!");
            resultLabel->setStyleSheet("QLabel { background-color: #f8d7da; padding: 10px; border: 1px solid #f5c6cb; }");
        }
    }
    
    void test3()
    {
        infoLabel->setText("Test 3: С проверкой видимости перед вызовом (ИСПРАВЛЕННЫЙ СПОСОБ)");
        resultLabel->setText("Результат: Выполняется...");
        QApplication::processEvents();
        
        try {
            // Убеждаемся, что виджет видим и активен перед показом диалога (важно для Windows)
            if (!isVisible() || !isActiveWindow()) {
                raise();
                activateWindow();
            }
            
            QMessageBox::StandardButton reply = QMessageBox::question(
                this, 
                "Info", 
                "Autocreate configuration folder?", 
                QMessageBox::Yes | QMessageBox::No
            );
            
            if (reply == QMessageBox::Yes) {
                resultLabel->setText("✅ Результат Test 3: УСПЕХ - Выбран Yes");
                resultLabel->setStyleSheet("QLabel { background-color: #d4edda; padding: 10px; border: 1px solid #c3e6cb; }");
            } else {
                resultLabel->setText("✅ Результат Test 3: УСПЕХ - Выбран No");
                resultLabel->setStyleSheet("QLabel { background-color: #d4edda; padding: 10px; border: 1px solid #c3e6cb; }");
            }
        } catch (...) {
            resultLabel->setText("❌ Результат Test 3: ОШИБКА - Исключение!");
            resultLabel->setStyleSheet("QLabel { background-color: #f8d7da; padding: 10px; border: 1px solid #f5c6cb; }");
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
