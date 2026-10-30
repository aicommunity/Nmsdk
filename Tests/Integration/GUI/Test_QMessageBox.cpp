#include <QApplication>
#include <QMainWindow>
#include <QPushButton>
#include <QVBoxLayout>
#include <QWidget>
#include <QMessageBox>
#include <QLabel>
#include <QDebug>
#include <QTimer>

class TestWindow : public QMainWindow
{
    Q_OBJECT

public:
    TestWindow(QWidget *parent = nullptr) : QMainWindow(parent)
    {
        setWindowTitle("QMessageBox Test - Windows");
        setMinimumSize(400, 300);
        
        QWidget *centralWidget = new QWidget(this);
        setCentralWidget(centralWidget);
        
        QVBoxLayout *layout = new QVBoxLayout(centralWidget);
        
        infoLabel = new QLabel("Нажмите кнопку для тестирования QMessageBox::question", this);
        infoLabel->setWordWrap(true);
        layout->addWidget(infoLabel);
        
        // Тест 1: Правильный способ с сохранением в переменную
        QPushButton *test1Button = new QPushButton("Test 1: StandardButton reply = QMessageBox::question(...)", this);
        connect(test1Button, &QPushButton::clicked, this, &TestWindow::test1);
        layout->addWidget(test1Button);
        
        // Тест 2: Прямое сравнение (проблемный способ)
        QPushButton *test2Button = new QPushButton("Test 2: Direct comparison (problematic)", this);
        connect(test2Button, &QPushButton::clicked, this, &TestWindow::test2);
        layout->addWidget(test2Button);
        
        // Тест 3: С проверкой видимости
        QPushButton *test3Button = new QPushButton("Test 3: With visibility check", this);
        connect(test3Button, &QPushButton::clicked, this, &TestWindow::test3);
        layout->addWidget(test3Button);
        
        // Тест 4: Множественные вызовы
        QPushButton *test4Button = new QPushButton("Test 4: Multiple calls", this);
        connect(test4Button, &QPushButton::clicked, this, &TestWindow::test4);
        layout->addWidget(test4Button);
        
        resultLabel = new QLabel("Результат: Ожидание...", this);
        resultLabel->setWordWrap(true);
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
                resultLabel->setText("Результат Test 1: УСПЕХ - Выбран Yes");
            } else {
                resultLabel->setText("Результат Test 1: УСПЕХ - Выбран No");
            }
        } catch (...) {
            resultLabel->setText("Результат Test 1: ОШИБКА - Исключение!");
        }
    }
    
    void test2()
    {
        infoLabel->setText("Test 2: Используется прямое сравнение (проблемный способ)");
        resultLabel->setText("Результат: Выполняется...");
        QApplication::processEvents();
        
        try {
            // Убеждаемся, что виджет видим и активен
            if (!isVisible() || !isActiveWindow()) {
                raise();
                activateWindow();
            }
            
            // Проблемный способ - прямое сравнение
            if (QMessageBox::question(this, "Info", "Close current config?", QMessageBox::Yes|QMessageBox::No) != QMessageBox::Yes) {
                resultLabel->setText("Результат Test 2: УСПЕХ - Выбран No (прямое сравнение работает)");
            } else {
                resultLabel->setText("Результат Test 2: УСПЕХ - Выбран Yes (прямое сравнение работает)");
            }
        } catch (...) {
            resultLabel->setText("Результат Test 2: ОШИБКА - Исключение при прямом сравнении!");
        }
    }
    
    void test3()
    {
        infoLabel->setText("Test 3: С проверкой видимости перед вызовом");
        resultLabel->setText("Результат: Выполняется...");
        QApplication::processEvents();
        
        try {
            // Убеждаемся, что виджет видим и активен перед показом диалога
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
                resultLabel->setText("Результат Test 3: УСПЕХ - Выбран Yes");
            } else {
                resultLabel->setText("Результат Test 3: УСПЕХ - Выбран No");
            }
        } catch (...) {
            resultLabel->setText("Результат Test 3: ОШИБКА - Исключение!");
        }
    }
    
    void test4()
    {
        infoLabel->setText("Test 4: Множественные последовательные вызовы");
        resultLabel->setText("Результат: Выполняется...");
        QApplication::processEvents();
        
        try {
            int yesCount = 0;
            int noCount = 0;
            
            for (int i = 0; i < 3; i++) {
                if (!isVisible() || !isActiveWindow()) {
                    raise();
                    activateWindow();
                }
                
                QMessageBox::StandardButton reply = QMessageBox::question(
                    this, 
                    "Info", 
                    QString("Question %1 of 3. Close current config?").arg(i + 1), 
                    QMessageBox::Yes | QMessageBox::No
                );
                
                if (reply == QMessageBox::Yes) {
                    yesCount++;
                } else {
                    noCount++;
                }
            }
            
            resultLabel->setText(QString("Результат Test 4: УСПЕХ - Yes: %1, No: %2").arg(yesCount).arg(noCount));
        } catch (...) {
            resultLabel->setText("Результат Test 4: ОШИБКА - Исключение!");
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

#include "Test_QMessageBox.moc"
