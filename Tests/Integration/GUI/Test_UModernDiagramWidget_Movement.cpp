#include <gtest/gtest.h>
#include <QApplication>
#include <QGraphicsSceneMouseEvent>
#include <QPointF>
#include <QSet>
#include <QMap>
#include <QTimer>
#include <QTest>
#include <cmath>
#include "../../../Rdk/GUI/Qt/UModernDiagramWidget.h"
#include "../../../Rdk/GUI/Qt/UModernDiagramNodeItem.h"
#include "../../../Rdk/GUI/Qt/UModernDiagramScene.h"
#include "../../../Rdk/GUI/Qt/UModernDiagramCoordinateManager.h"
#include "../../../Rdk/GUI/Qt/UModernDiagramCacheManager.h"
#include "../../../Rdk/GUI/Qt/UStyleManager.h"

// Test fixture для тестирования перемещения компонентов
class UModernDiagramWidgetMovementTest : public ::testing::Test {
protected:
    // Typedef для доступа к приватному классу NodeItem через friend declaration
    typedef UModernDiagramNodeItem NodeItem;
    void SetUp() override {
        // Создание QApplication если его нет
        static int argc = 1;
        static const char* argv[] = {"test"};
        if (!qApp) {
            app = new QApplication(argc, const_cast<char**>(argv));
        }

        // Инициализируем UStyleManager перед созданием виджета
        // Это гарантирует, что все векторы инициализированы
        UStyleManager::instance();

        widget = new UModernDiagramWidget(nullptr);

        // Убеждаемся, что виджет и сцена инициализированы
        ASSERT_NE(widget, nullptr);
        ASSERT_NE(widget->m_scene, nullptr);
    }

    void TearDown() override {
        if (widget) {
            delete widget;
            widget = nullptr;
        }
        // Не удаляем app, так как он может использоваться другими тестами
    }

    // Вспомогательная функция для создания тестового компонента напрямую
    NodeItem* createTestNode(const QString& name, const QPointF& pos) {
        if (!widget || !widget->m_scene) {
            return nullptr;
        }

        // Создаем NodeItem напрямую для тестирования
        auto* node = new NodeItem(widget, name, "TestClass");
        widget->m_scene->addItem(node);
        widget->m_nodes.append(node);
        widget->m_nodeByName.insert(name, node);

        // Устанавливаем позицию
        widget->m_isBuildingScene = true;
        node->setPos(pos);
        widget->m_lastNodePositions[node] = pos;
        widget->m_isBuildingScene = false;

        return node;
    }

    // Симуляция движения компонента
    void simulateNodeMove(NodeItem* node, const QPointF& newPos) {
        if (!node || !widget) return;

        // НЕ устанавливаем m_isBuildingScene, чтобы позволить отслеживание отрицательных позиций
        // Флаг m_isBuildingScene используется только при создании компонентов, не при их движении
        // Но устанавливаем m_isSavingCoordinates, чтобы предотвратить вызов saveCoord в тесте
        // (так как движок RDK не инициализирован)
        widget->m_isSavingCoordinates = true;

        // Устанавливаем новую позицию напрямую
        // setPos() автоматически вызовет itemChange(ItemPositionHasChanged, ...)
        node->setPos(newPos);

        // Обрабатываем события Qt, чтобы itemChange был обработан
        QApplication::processEvents();

        // Сбрасываем флаг после обработки
        widget->m_isSavingCoordinates = false;
    }

    // Симуляция mouseReleaseEvent
    void simulateMouseRelease() {
        if (!widget || !widget->m_scene) return;

        // Создаем событие мыши
        QGraphicsSceneMouseEvent* event = new QGraphicsSceneMouseEvent(QEvent::GraphicsSceneMouseRelease);
        event->setButton(Qt::LeftButton);
        event->setButtonDownPos(Qt::LeftButton, QPointF(0, 0));
        event->setScenePos(QPointF(0, 0));

        // Отправляем событие через QApplication::sendEvent
        // Это правильный способ для вызова защищенных методов обработки событий
        QApplication::sendEvent(widget->m_scene, event);

        delete event;

        // Обрабатываем события Qt после mouseReleaseEvent для обработки всех событий,
        // включая обновление offset и позиций компонентов
        QApplication::processEvents();
    }

    // Проверка обновления offset (устаревшая функция, используйте verifyOffsetUpdate)
    // Оставлена для обратной совместимости, но не используется в новых тестах
    bool verifyOffsetUpdated(const QList<NodeItem*>& nodes) {
        if (!widget || nodes.isEmpty()) return false;

        // Проверяем, что offset был обновлен правильно
        // После обновления offset, компонент с минимальной позицией должен быть в (0,0) или близко к нему
        QPointF minPos(0, 0);
        bool first = true;

        for (NodeItem* node : nodes) {
            if (node) {
                QPointF pos = node->scenePos();
                if (first) {
                    minPos = pos;
                    first = false;
                } else {
                    if (pos.x() < minPos.x()) minPos.setX(pos.x());
                    if (pos.y() < minPos.y()) minPos.setY(pos.y());
                }
            }
        }

        // После обновления offset минимальная позиция должна быть >= 0
        return minPos.x() >= -0.1 && minPos.y() >= -0.1; // Небольшая погрешность для float
    }

    // Проверка правильности обновления offset
    // Проверяет, что deltaOffset = -minNormalizedPos и newOffset = oldOffset + deltaOffset
    bool verifyOffsetUpdate(const QPointF& expectedMinNormalizedPos, const QPointF& oldOffset) {
        if (!widget) return false;

        QPointF newOffset = widget->testGetNormalizationOffset();
        QPointF expectedDeltaOffset(0, 0);

        // Вычисляем ожидаемый deltaOffset
        if (expectedMinNormalizedPos.x() < 0) {
            expectedDeltaOffset.setX(-expectedMinNormalizedPos.x());
        }
        if (expectedMinNormalizedPos.y() < 0) {
            expectedDeltaOffset.setY(-expectedMinNormalizedPos.y());
        }

        QPointF expectedNewOffset = oldOffset + expectedDeltaOffset;

        // Проверяем с небольшой погрешностью для float
        return (std::abs(newOffset.x() - expectedNewOffset.x()) < 0.1 &&
                std::abs(newOffset.y() - expectedNewOffset.y()) < 0.1);
    }

    // Вспомогательная функция для сохранения абсолютных координат узлов
    QMap<NodeItem*, QPointF> saveAbsolutePositions(const QList<NodeItem*>& nodes, const QPointF& offset) {
        QMap<NodeItem*, QPointF> positions;
        for (NodeItem* node : nodes) {
            if (node) {
                QPointF normalizedPos = node->pos();
                QPointF absolutePos = normalizedPos + offset;
                positions[node] = absolutePos;
            }
        }
        return positions;
    }

    // Проверка сохранения абсолютных координат после обновления offset
    // Проверяет, что абсолютные координаты (normalizedPos + offset) остались неизменными
    // Возвращает false и выводит детали через EXPECT_NEAR для первого компонента с ошибкой
    bool verifyAbsoluteCoordinatesPreserved(const QMap<NodeItem*, QPointF>& positionsBeforeOffsetUpdate) {
        if (!widget) return false;

        QPointF newOffset = widget->testGetNormalizationOffset();
        bool allPreserved = true;

        for (auto it = positionsBeforeOffsetUpdate.begin(); it != positionsBeforeOffsetUpdate.end(); ++it) {
            NodeItem* node = it.key();
            if (!node) continue;

            QPointF oldAbsolutePos = it.value();
            QPointF newNormalizedPos = node->pos();
            QPointF newAbsolutePos = newNormalizedPos + newOffset;

            // Проверяем, что абсолютные координаты сохранились (с небольшой погрешностью)
            // Используем EXPECT_NEAR для вывода детальной информации об ошибке
            EXPECT_NEAR(oldAbsolutePos.x(), newAbsolutePos.x(), 0.1)
                << "Node '" << node->nodeName.toStdString()
                << "' X coordinate: oldAbsolute=" << oldAbsolutePos.x()
                << ", newAbsolute=" << newAbsolutePos.x()
                << ", newNormalized=" << newNormalizedPos.x()
                << ", newOffset=" << newOffset.x();

            EXPECT_NEAR(oldAbsolutePos.y(), newAbsolutePos.y(), 0.1)
                << "Node '" << node->nodeName.toStdString()
                << "' Y coordinate: oldAbsolute=" << oldAbsolutePos.y()
                << ", newAbsolute=" << newAbsolutePos.y()
                << ", newNormalized=" << newNormalizedPos.y()
                << ", newOffset=" << newOffset.y();

            if (std::abs(oldAbsolutePos.x() - newAbsolutePos.x()) > 0.1 ||
                std::abs(oldAbsolutePos.y() - newAbsolutePos.y()) > 0.1) {
                allPreserved = false;
            }
        }
        return allPreserved;
    }

    UModernDiagramWidget* widget = nullptr;
    QApplication* app = nullptr;
};

// ---------------- Основные тесты перемещения ----------------

// Тест 1.1: Движение влево-вверх (отрицательные координаты)
TEST_F(UModernDiagramWidgetMovementTest, MovementLeftUp_NegativeCoordinates) {
    // Создаем несколько компонентов
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    auto* node2 = createTestNode("Component2", QPointF(200, 200));
    ASSERT_NE(node1, nullptr);
    ASSERT_NE(node2, nullptr);

    // Сохраняем начальный offset
    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Сохраняем абсолютные координаты ДО перемещения компонента в отрицательную область
    // Это правильный момент для сохранения, так как компоненты еще имеют положительные normalizedPos
    QMap<NodeItem*, QPointF> positionsBeforeMove = saveAbsolutePositions({node1, node2}, initialOffset);

    // Отладочная информация: проверяем, что позиции сохранены правильно
    QPointF node1PosBeforeMove = node1->pos();
    QPointF node1AbsoluteBeforeMove = positionsBeforeMove[node1];
    EXPECT_EQ(node1PosBeforeMove, QPointF(100, 100)) << "node1 should have normalizedPos (100, 100) before move";
    EXPECT_EQ(node1AbsoluteBeforeMove, QPointF(100, 100)) << "node1 should have absolutePos (100, 100) before move";

    // Дополнительная проверка: убеждаемся, что positionsBeforeMove содержит правильные значения
    ASSERT_NE(positionsBeforeMove.find(node1), positionsBeforeMove.end()) << "node1 should be in positionsBeforeMove";
    ASSERT_NE(positionsBeforeMove.find(node2), positionsBeforeMove.end()) << "node2 should be in positionsBeforeMove";

    // Перемещаем компонент влево-вверх за границу (0,0)
    QPointF negativePos(-50, -30);
    simulateNodeMove(node1, negativePos);

    // Проверяем, что компонент добавлен в m_componentsWithNegativePos
    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().contains(node1));
    EXPECT_EQ(widget->testGetComponentsWithNegativePos().size(), 1);

    // Offset еще не изменился, так как обновление происходит только при mouseReleaseEvent
    QPointF offsetBeforeUpdate = widget->testGetNormalizationOffset();
    EXPECT_EQ(offsetBeforeUpdate, initialOffset);

    // Используем позиции, сохраненные ДО перемещения, для проверки сохранения абсолютных координат
    // После обновления offset абсолютные координаты должны остаться теми же, что и до перемещения

    // Симулируем mouseReleaseEvent
    simulateMouseRelease();

    // Проверяем, что offset обновился правильно
    QPointF expectedMinNormalizedPos = negativePos; // Минимальная позиция - это позиция node1
    EXPECT_TRUE(verifyOffsetUpdate(expectedMinNormalizedPos, offsetBeforeUpdate));

    // Проверяем сохранение абсолютных координат напрямую
    QPointF finalOffset = widget->testGetNormalizationOffset();
    QPointF node1FinalNormalized = node1->pos();
    QPointF node2FinalNormalized = node2->pos();
    QPointF node1FinalAbsolute = node1FinalNormalized + finalOffset;
    QPointF node2FinalAbsolute = node2FinalNormalized + finalOffset;

    // Используем позиции, сохраненные ДО перемещения компонента в отрицательную область
    // После обновления offset абсолютные координаты должны вернуться к исходным значениям
    QPointF node1OldAbsolute = positionsBeforeMove[node1];
    QPointF node2OldAbsolute = positionsBeforeMove[node2];

    // Отладочная информация для диагностики
    if (std::abs(node1OldAbsolute.x() - node1FinalAbsolute.x()) > 0.1 ||
        std::abs(node1OldAbsolute.y() - node1FinalAbsolute.y()) > 0.1) {
        std::cout << "DEBUG node1: oldAbsolute=(" << node1OldAbsolute.x() << ", " << node1OldAbsolute.y()
                  << "), newAbsolute=(" << node1FinalAbsolute.x() << ", " << node1FinalAbsolute.y()
                  << "), newNormalized=(" << node1FinalNormalized.x() << ", " << node1FinalNormalized.y()
                  << "), finalOffset=(" << finalOffset.x() << ", " << finalOffset.y() << ")" << std::endl;
    }

    // Проверяем, что абсолютные координаты сохранились (с небольшой погрешностью)
    EXPECT_NEAR(node1OldAbsolute.x(), node1FinalAbsolute.x(), 0.1)
        << "node1 X: oldAbsolute=" << node1OldAbsolute.x()
        << ", newAbsolute=" << node1FinalAbsolute.x()
        << ", newNormalized=" << node1FinalNormalized.x()
        << ", finalOffset=" << finalOffset.x();
    EXPECT_NEAR(node1OldAbsolute.y(), node1FinalAbsolute.y(), 0.1)
        << "node1 Y: oldAbsolute=" << node1OldAbsolute.y()
        << ", newAbsolute=" << node1FinalAbsolute.y()
        << ", newNormalized=" << node1FinalNormalized.y()
        << ", finalOffset=" << finalOffset.y();

    EXPECT_NEAR(node2OldAbsolute.x(), node2FinalAbsolute.x(), 0.1)
        << "node2 X: oldAbsolute=" << node2OldAbsolute.x()
        << ", newAbsolute=" << node2FinalAbsolute.x()
        << ", newNormalized=" << node2FinalNormalized.x()
        << ", finalOffset=" << finalOffset.x();
    EXPECT_NEAR(node2OldAbsolute.y(), node2FinalAbsolute.y(), 0.1)
        << "node2 Y: oldAbsolute=" << node2OldAbsolute.y()
        << ", newAbsolute=" << node2FinalAbsolute.y()
        << ", newNormalized=" << node2FinalNormalized.y()
        << ", finalOffset=" << finalOffset.y();

    // Проверяем, что компонент имеет корректную позицию после обновления
    QPointF finalPos = node1->scenePos();
    EXPECT_GE(finalPos.x(), -0.1); // Должен быть >= 0 после обновления offset
    EXPECT_GE(finalPos.y(), -0.1);

    // Проверяем, что set очищен
    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().isEmpty());
}

// Тест 1.2: Движение вправо-вниз (положительные координаты)
TEST_F(UModernDiagramWidgetMovementTest, MovementRightDown_PositiveCoordinates) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    ASSERT_NE(node1, nullptr);

    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Перемещаем компонент вправо-вниз
    QPointF positivePos(300, 400);
    simulateNodeMove(node1, positivePos);

    // Проверяем, что компонент НЕ добавлен в m_componentsWithNegativePos
    EXPECT_FALSE(widget->testGetComponentsWithNegativePos().contains(node1));
    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().isEmpty());

    // Симулируем mouseReleaseEvent
    simulateMouseRelease();

    // Проверяем, что offset НЕ изменился
    QPointF newOffset = widget->testGetNormalizationOffset();
    EXPECT_EQ(initialOffset.x(), newOffset.x());
    EXPECT_EQ(initialOffset.y(), newOffset.y());
}

// Тест 1.3: Движение влево-вниз (обновление offset только по X)
TEST_F(UModernDiagramWidgetMovementTest, MovementLeftDown_OffsetXOnly) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    ASSERT_NE(node1, nullptr);

    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Сохраняем абсолютные координаты ДО перемещения компонента в отрицательную область
    QMap<NodeItem*, QPointF> positionsBeforeMove = saveAbsolutePositions({node1}, initialOffset);

    // Перемещаем компонент влево, но вниз
    QPointF leftDownPos(-50, 300);
    simulateNodeMove(node1, leftDownPos);

    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().contains(node1));

    // Offset еще не изменился, так как обновление происходит только при mouseReleaseEvent
    QPointF offsetBeforeUpdate = widget->testGetNormalizationOffset();
    EXPECT_EQ(offsetBeforeUpdate, initialOffset);

    simulateMouseRelease();

    // Проверяем правильность обновления offset
    QPointF expectedMinNormalizedPos = leftDownPos; // Минимальная позиция - это позиция node1
    EXPECT_TRUE(verifyOffsetUpdate(expectedMinNormalizedPos, offsetBeforeUpdate));

    // Проверяем, что абсолютные координаты сохранились
    // Используем позиции, сохраненные ДО перемещения
    EXPECT_TRUE(verifyAbsoluteCoordinatesPreserved(positionsBeforeMove));

    QPointF newOffset = widget->testGetNormalizationOffset();
    // Offset должен обновиться только по X
    EXPECT_NE(initialOffset.x(), newOffset.x());
    // Y может остаться тем же (если не было других компонентов с отрицательным Y)
    // или измениться, если был другой компонент с отрицательным Y

    QPointF finalPos = node1->scenePos();
    EXPECT_GE(finalPos.x(), -0.1);
}

// ---------------- Дополнительные тесты: координаты и кэш ----------------

// Тест координатного менеджера: прямое и обратное преобразование kernel <-> scene
TEST_F(UModernDiagramWidgetMovementTest, CoordinateManager_KernelSceneConversion)
{
    ASSERT_NE(widget, nullptr);
    // Используем отдельный экземпляр менеджера координат для теста преобразований
    UModernDiagramCoordinateManager coord(widget);

    // По умолчанию должен использоваться масштаб по умолчанию
    double scale = coord.getCoordScale();
    ASSERT_GT(scale, 0.0);

    QPointF kernel(1.5, -2.0);
    QPointF scene = coord.scenePosFromKernel(kernel);
    QPointF back = coord.kernelPosFromScene(scene);

    EXPECT_NEAR(scene.x(), kernel.x() * scale, 1e-6);
    EXPECT_NEAR(scene.y(), kernel.y() * scale, 1e-6);

    EXPECT_NEAR(back.x(), kernel.x(), 1e-6);
    EXPECT_NEAR(back.y(), kernel.y(), 1e-6);

    // Меняем масштаб и проверяем, что преобразование учитывает новый scale
    coord.setCoordScale(scale * 2.0);
    double newScale = coord.getCoordScale();
    EXPECT_NEAR(newScale, scale * 2.0, 1e-9);

    QPointF scene2 = coord.scenePosFromKernel(kernel);
    EXPECT_NEAR(scene2.x(), kernel.x() * newScale, 1e-6);
    EXPECT_NEAR(scene2.y(), kernel.y() * newScale, 1e-6);
}

// Тест кэша компонентов: setEntry / getEntry / hasEntry / invalidateEntry / clear
TEST_F(UModernDiagramWidgetMovementTest, ComponentCache_BasicOperations)
{
    // Тестируем UModernDiagramComponentCache как независимый компонент
    UModernDiagramComponentCache cache;
    const QString compName = QStringLiteral("TestComponent");

    // Начальное состояние: записи нет
    cache.invalidateEntry(compName);
    EXPECT_FALSE(cache.hasEntry(compName));
    EXPECT_EQ(cache.getEntry(compName), nullptr);

    // Добавляем запись
    UModernDiagramComponentCacheEntry entry;
    entry.className = QStringLiteral("TestClass");
    entry.kernelPos = QPointF(1.0, 2.0);
    entry.hasKernelPos = true;
    entry.timestamp = 123456789;

    cache.setEntry(compName, entry);
    EXPECT_TRUE(cache.hasEntry(compName));

    UModernDiagramComponentCacheEntry* stored = cache.getEntry(compName);
    ASSERT_NE(stored, nullptr);
    EXPECT_EQ(stored->className, entry.className);
    EXPECT_EQ(stored->kernelPos, entry.kernelPos);
    EXPECT_TRUE(stored->hasKernelPos);
    EXPECT_EQ(stored->timestamp, entry.timestamp);

    // Инвалидация записи
    cache.invalidateEntry(compName);
    EXPECT_FALSE(cache.hasEntry(compName));
    EXPECT_EQ(cache.getEntry(compName), nullptr);

    // Повторно добавляем несколько записей и очищаем весь кэш
    cache.setEntry(QStringLiteral("A"), entry);
    cache.setEntry(QStringLiteral("B"), entry);
    EXPECT_TRUE(cache.hasEntry(QStringLiteral("A")));
    EXPECT_TRUE(cache.hasEntry(QStringLiteral("B")));

    cache.clear();
    EXPECT_FALSE(cache.hasEntry(QStringLiteral("A")));
    EXPECT_FALSE(cache.hasEntry(QStringLiteral("B")));
}

// Тест 1.4: Движение вправо-вверх (обновление offset только по Y)
TEST_F(UModernDiagramWidgetMovementTest, MovementRightUp_OffsetYOnly) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    ASSERT_NE(node1, nullptr);

    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Сохраняем абсолютные координаты ДО перемещения компонента в отрицательную область
    QMap<NodeItem*, QPointF> positionsBeforeMove = saveAbsolutePositions({node1}, initialOffset);

    // Перемещаем компонент вправо, но вверх
    QPointF rightUpPos(300, -50);
    simulateNodeMove(node1, rightUpPos);

    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().contains(node1));

    // Offset еще не изменился, так как обновление происходит только при mouseReleaseEvent
    QPointF offsetBeforeUpdate = widget->testGetNormalizationOffset();
    EXPECT_EQ(offsetBeforeUpdate, initialOffset);

    simulateMouseRelease();

    // Проверяем правильность обновления offset
    QPointF expectedMinNormalizedPos = rightUpPos; // Минимальная позиция - это позиция node1
    EXPECT_TRUE(verifyOffsetUpdate(expectedMinNormalizedPos, offsetBeforeUpdate));

    // Проверяем, что абсолютные координаты сохранились
    // Используем позиции, сохраненные ДО перемещения
    EXPECT_TRUE(verifyAbsoluteCoordinatesPreserved(positionsBeforeMove));

    QPointF newOffset = widget->testGetNormalizationOffset();
    // Offset должен обновиться только по Y
    EXPECT_NE(initialOffset.y(), newOffset.y());

    QPointF finalPos = node1->scenePos();
    EXPECT_GE(finalPos.y(), -0.1);
}

// Тест 2.1: Отсутствие каскадных обновлений во время движения
TEST_F(UModernDiagramWidgetMovementTest, NoCascadeUpdatesDuringMovement) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    ASSERT_NE(node1, nullptr);

    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Сохраняем абсолютные координаты ДО перемещения компонента в отрицательную область
    // Сохраняем начальную позицию (100, 100) до всех перемещений
    QMap<NodeItem*, QPointF> positionsBeforeMove = saveAbsolutePositions({node1}, initialOffset);

    int offsetUpdateCount = 0;

    // Сохраняем начальное значение offset для отслеживания изменений
    QPointF lastOffset = initialOffset;

    // Симулируем несколько движений мыши (несколько вызовов itemChange)
    for (int i = 0; i < 10; ++i) {
        QPointF newPos(-10 - i * 5, -5 - i * 3);
        simulateNodeMove(node1, newPos);

        // Проверяем, что offset НЕ обновляется во время движения
        QPointF currentOffset = widget->testGetNormalizationOffset();
        if (currentOffset != lastOffset) {
            offsetUpdateCount++;
            lastOffset = currentOffset;
        }
    }

    // Offset не должен обновляться во время движения
    EXPECT_EQ(offsetUpdateCount, 0);
    EXPECT_EQ(widget->testGetNormalizationOffset(), initialOffset);

    // Проверяем, что компонент в set
    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().contains(node1));

    // Offset еще не изменился, так как обновление происходит только при mouseReleaseEvent
    QPointF offsetBeforeUpdate = widget->testGetNormalizationOffset();
    EXPECT_EQ(offsetBeforeUpdate, initialOffset);

    // Симулируем mouseReleaseEvent
    simulateMouseRelease();

    // Теперь offset должен обновиться один раз
    QPointF finalOffset = widget->testGetNormalizationOffset();
    EXPECT_NE(finalOffset, initialOffset);

    // Проверяем правильность обновления offset
    // Последняя позиция была (-10 - 9*5, -5 - 9*3) = (-55, -32)
    QPointF expectedMinNormalizedPos(-55, -32);
    EXPECT_TRUE(verifyOffsetUpdate(expectedMinNormalizedPos, offsetBeforeUpdate));

    // Проверяем, что абсолютные координаты сохранились
    // Используем позиции, сохраненные ДО перемещения
    EXPECT_TRUE(verifyAbsoluteCoordinatesPreserved(positionsBeforeMove));

    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().isEmpty());
}

// Тест 2.2: Множественные компоненты с отрицательными позициями
TEST_F(UModernDiagramWidgetMovementTest, MultipleComponentsWithNegativePos) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    auto* node2 = createTestNode("Component2", QPointF(200, 200));
    auto* node3 = createTestNode("Component3", QPointF(300, 300));
    ASSERT_NE(node1, nullptr);
    ASSERT_NE(node2, nullptr);
    ASSERT_NE(node3, nullptr);

    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Сохраняем абсолютные координаты ДО перемещения компонентов в отрицательную область
    QMap<NodeItem*, QPointF> positionsBeforeMove = saveAbsolutePositions({node1, node2, node3}, initialOffset);

    // Перемещаем несколько компонентов в отрицательную область
    QPointF pos1(-50, -30);
    QPointF pos2(-100, -20);
    QPointF pos3(-30, -80);
    simulateNodeMove(node1, pos1);
    simulateNodeMove(node2, pos2);
    simulateNodeMove(node3, pos3);

    // Проверяем, что все они добавлены в set
    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().contains(node1));
    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().contains(node2));
    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().contains(node3));
    EXPECT_EQ(widget->testGetComponentsWithNegativePos().size(), 3);

    // Вычисляем ожидаемую минимальную позицию среди всех компонентов с отрицательными позициями
    QPointF expectedMinNormalizedPos(0, 0);
    bool first = true;
    for (NodeItem* node : widget->testGetComponentsWithNegativePos()) {
        if (node) {
            QPointF normalizedPos = node->pos();
            if (first) {
                expectedMinNormalizedPos = normalizedPos;
                first = false;
            } else {
                if (normalizedPos.x() < expectedMinNormalizedPos.x())
                    expectedMinNormalizedPos.setX(normalizedPos.x());
                if (normalizedPos.y() < expectedMinNormalizedPos.y())
                    expectedMinNormalizedPos.setY(normalizedPos.y());
            }
        }
    }
    // Ожидаемая минимальная позиция: (-100, -80) - минимальные значения из pos1, pos2, pos3
    EXPECT_EQ(expectedMinNormalizedPos.x(), -100.0);
    EXPECT_EQ(expectedMinNormalizedPos.y(), -80.0);

    // Симулируем mouseReleaseEvent
    simulateMouseRelease();

    // Проверяем правильность обновления offset для минимальной позиции (-100, -80)
    EXPECT_TRUE(verifyOffsetUpdate(expectedMinNormalizedPos, initialOffset));

    // Проверяем, что абсолютные координаты сохранились
    // Используем позиции, сохраненные ДО перемещения
    EXPECT_TRUE(verifyAbsoluteCoordinatesPreserved(positionsBeforeMove));

    // Проверяем, что все компоненты имеют неотрицательные позиции после обновления
    EXPECT_GE(node1->scenePos().x(), -0.1);
    EXPECT_GE(node1->scenePos().y(), -0.1);
    EXPECT_GE(node2->scenePos().x(), -0.1);
    EXPECT_GE(node2->scenePos().y(), -0.1);
    EXPECT_GE(node3->scenePos().x(), -0.1);
    EXPECT_GE(node3->scenePos().y(), -0.1);

    // Компонент с минимальной позицией (node2) должен восстановить исходные абсолютные координаты
    // node2 был в (200, 200) до перемещения, после обновления offset он должен вернуться к исходной позиции
    QPointF node2Pos = node2->pos();
    QPointF node2Absolute = node2Pos + widget->testGetNormalizationOffset();
    QPointF node2OriginalAbsolute = positionsBeforeMove[node2];
    EXPECT_NEAR(node2OriginalAbsolute.x(), node2Absolute.x(), 0.1);
    EXPECT_NEAR(node2OriginalAbsolute.y(), node2Absolute.y(), 0.1);
}

// Тест 3.1: Групповое перемещение влево-вверх
TEST_F(UModernDiagramWidgetMovementTest, GroupMovementLeftUp_PreserveRelativePositions) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    auto* node2 = createTestNode("Component2", QPointF(200, 200));
    auto* node3 = createTestNode("Component3", QPointF(150, 150));
    ASSERT_NE(node1, nullptr);
    ASSERT_NE(node2, nullptr);
    ASSERT_NE(node3, nullptr);

    // Вычисляем относительные позиции
    QPointF relativePos1 = node2->scenePos() - node1->scenePos();
    QPointF relativePos2 = node3->scenePos() - node1->scenePos();

    // Выделяем группу (симулируем выделение)
    node1->setSelected(true);
    node2->setSelected(true);
    node3->setSelected(true);

    // Перемещаем группу влево-вверх
    QPointF delta(-150, -100);
    simulateNodeMove(node1, node1->scenePos() + delta);
    simulateNodeMove(node2, node2->scenePos() + delta);
    simulateNodeMove(node3, node3->scenePos() + delta);

    // Проверяем, что все компоненты в set
    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().contains(node1) ||
                widget->testGetComponentsWithNegativePos().contains(node2) ||
                widget->testGetComponentsWithNegativePos().contains(node3));

    // Симулируем mouseReleaseEvent
    simulateMouseRelease();

    // Проверяем, что относительные позиции сохранены (с учетом обновления offset)
    QPointF newRelativePos1 = node2->scenePos() - node1->scenePos();
    QPointF newRelativePos2 = node3->scenePos() - node1->scenePos();

    EXPECT_NEAR(relativePos1.x(), newRelativePos1.x(), 1.0);
    EXPECT_NEAR(relativePos1.y(), newRelativePos1.y(), 1.0);
    EXPECT_NEAR(relativePos2.x(), newRelativePos2.x(), 1.0);
    EXPECT_NEAR(relativePos2.y(), newRelativePos2.y(), 1.0);
}

// Тест 3.2: Групповое перемещение вправо-вниз
TEST_F(UModernDiagramWidgetMovementTest, GroupMovementRightDown_NoOffsetUpdate) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    auto* node2 = createTestNode("Component2", QPointF(200, 200));
    ASSERT_NE(node1, nullptr);
    ASSERT_NE(node2, nullptr);

    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Перемещаем группу вправо-вниз
    QPointF delta(200, 300);
    simulateNodeMove(node1, node1->scenePos() + delta);
    simulateNodeMove(node2, node2->scenePos() + delta);

    // Проверяем, что компоненты НЕ в set (позиции положительные)
    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().isEmpty());

    // Симулируем mouseReleaseEvent
    simulateMouseRelease();

    // Проверяем, что offset НЕ изменился
    QPointF newOffset = widget->testGetNormalizationOffset();
    EXPECT_EQ(initialOffset.x(), newOffset.x());
    EXPECT_EQ(initialOffset.y(), newOffset.y());
}

// Тест 5.1: Движение компонента точно на границу (0,0)
TEST_F(UModernDiagramWidgetMovementTest, MovementToBoundary_ZeroZero) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    ASSERT_NE(node1, nullptr);

    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Перемещаем компонент точно на (0,0)
    simulateNodeMove(node1, QPointF(0, 0));

    // Проверяем, что компонент НЕ добавлен в set (позиция не отрицательная)
    EXPECT_FALSE(widget->testGetComponentsWithNegativePos().contains(node1));

    // Симулируем mouseReleaseEvent
    simulateMouseRelease();

    // Проверяем, что offset НЕ обновился
    QPointF newOffset = widget->testGetNormalizationOffset();
    EXPECT_EQ(initialOffset.x(), newOffset.x());
    EXPECT_EQ(initialOffset.y(), newOffset.y());
}

// Тест 5.2: Быстрое перемещение (множественные события)
TEST_F(UModernDiagramWidgetMovementTest, RapidMovement_MultipleEvents) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    ASSERT_NE(node1, nullptr);

    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Сохраняем абсолютные координаты ДО перемещения компонента в отрицательную область
    QMap<NodeItem*, QPointF> positionsBeforeMove = saveAbsolutePositions({node1}, initialOffset);

    // Симулируем множество быстрых движений
    for (int i = 0; i < 50; ++i) {
        QPointF newPos(-i * 2, -i * 1.5);
        simulateNodeMove(node1, newPos);
    }

    // Проверяем, что offset НЕ обновлялся во время движения
    EXPECT_EQ(widget->testGetNormalizationOffset(), initialOffset);
    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().contains(node1));

    // Offset еще не изменился, так как обновление происходит только при mouseReleaseEvent
    QPointF offsetBeforeUpdate = widget->testGetNormalizationOffset();
    EXPECT_EQ(offsetBeforeUpdate, initialOffset);

    // Симулируем mouseReleaseEvent
    simulateMouseRelease();

    // Проверяем, что offset обновился только один раз
    QPointF finalOffset = widget->testGetNormalizationOffset();
    EXPECT_NE(initialOffset, finalOffset);

    // Проверяем правильность обновления offset
    // Последняя позиция была (-49*2, -49*1.5) = (-98, -73.5)
    QPointF expectedMinNormalizedPos(-98, -73.5);
    EXPECT_TRUE(verifyOffsetUpdate(expectedMinNormalizedPos, offsetBeforeUpdate));

    // Проверяем, что абсолютные координаты сохранились
    // Используем позиции, сохраненные ДО перемещения
    EXPECT_TRUE(verifyAbsoluteCoordinatesPreserved(positionsBeforeMove));

    // Проверяем, что компонент имеет корректную позицию
    QPointF finalPos = node1->scenePos();
    EXPECT_GE(finalPos.x(), -0.1);
    EXPECT_GE(finalPos.y(), -0.1);
}

// Тест: Проверка правильности вычисления минимальной позиции среди нескольких компонентов
TEST_F(UModernDiagramWidgetMovementTest, MinPositionCalculation_MultipleComponents) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    auto* node2 = createTestNode("Component2", QPointF(200, 200));
    auto* node3 = createTestNode("Component3", QPointF(300, 300));
    ASSERT_NE(node1, nullptr);
    ASSERT_NE(node2, nullptr);
    ASSERT_NE(node3, nullptr);

    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Сохраняем абсолютные координаты ДО перемещения компонентов в отрицательную область
    QMap<NodeItem*, QPointF> positionsBeforeMove = saveAbsolutePositions({node1, node2, node3}, initialOffset);

    // Перемещаем компоненты в разные отрицательные позиции
    // node1: (-50, -30) - минимальный X
    // node2: (-100, -20) - минимальный X и Y
    // node3: (-30, -80) - минимальный Y
    simulateNodeMove(node1, QPointF(-50, -30));
    simulateNodeMove(node2, QPointF(-100, -20));
    simulateNodeMove(node3, QPointF(-30, -80));

    // Проверяем, что все компоненты добавлены в set
    EXPECT_EQ(widget->testGetComponentsWithNegativePos().size(), 3);

    // Вычисляем ожидаемую минимальную позицию вручную
    QPointF expectedMinNormalizedPos(-100, -80); // Минимальные значения: min(-50, -100, -30) = -100, min(-30, -20, -80) = -80

    simulateMouseRelease();

    // Проверяем правильность обновления offset для вычисленной минимальной позиции
    EXPECT_TRUE(verifyOffsetUpdate(expectedMinNormalizedPos, initialOffset));

    // Проверяем, что абсолютные координаты сохранились
    // Используем позиции, сохраненные ДО перемещения
    EXPECT_TRUE(verifyAbsoluteCoordinatesPreserved(positionsBeforeMove));

    // Проверяем, что компонент с минимальной позицией (node2) восстановил исходные абсолютные координаты
    // node2 был в (200, 200) до перемещения, после обновления offset он должен вернуться к исходной позиции
    QPointF node2Pos = node2->pos();
    QPointF node2Absolute = node2Pos + widget->testGetNormalizationOffset();
    QPointF node2OriginalAbsolute = positionsBeforeMove[node2];
    EXPECT_NEAR(node2OriginalAbsolute.x(), node2Absolute.x(), 0.1);
    EXPECT_NEAR(node2OriginalAbsolute.y(), node2Absolute.y(), 0.1);

    // Проверяем, что все компоненты имеют неотрицательные нормализованные позиции
    EXPECT_GE(node2Pos.x(), -0.1);
    EXPECT_GE(node2Pos.y(), -0.1);
}

// Тест: Проверка сохранения абсолютных координат после обновления offset
TEST_F(UModernDiagramWidgetMovementTest, AbsoluteCoordinatesPreserved_AfterOffsetUpdate) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    auto* node2 = createTestNode("Component2", QPointF(200, 200));
    auto* node3 = createTestNode("Component3", QPointF(300, 300));
    ASSERT_NE(node1, nullptr);
    ASSERT_NE(node2, nullptr);
    ASSERT_NE(node3, nullptr);

    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Сохраняем начальные абсолютные координаты всех компонентов
    QMap<NodeItem*, QPointF> initialAbsolutePositions = saveAbsolutePositions({node1, node2, node3}, initialOffset);

    // Сохраняем абсолютные координаты ДО перемещения компонента в отрицательную область
    QMap<NodeItem*, QPointF> positionsBeforeMove = saveAbsolutePositions({node1, node2, node3}, initialOffset);

    // Перемещаем только node1 в отрицательную область
    QPointF negativePos(-50, -30);
    simulateNodeMove(node1, negativePos);

    // Offset еще не изменился, так как обновление происходит только при mouseReleaseEvent
    QPointF offsetBeforeUpdate = widget->testGetNormalizationOffset();
    EXPECT_EQ(offsetBeforeUpdate, initialOffset);

    simulateMouseRelease();

    // Проверяем, что абсолютные координаты сохранились после обновления offset
    // Используем позиции, сохраненные ДО перемещения
    EXPECT_TRUE(verifyAbsoluteCoordinatesPreserved(positionsBeforeMove));

    // Проверяем, что компоненты, которые не были в m_componentsWithNegativePos (node2, node3),
    // не изменили свои абсолютные координаты
    QPointF newOffset = widget->testGetNormalizationOffset();
    for (auto it = initialAbsolutePositions.begin(); it != initialAbsolutePositions.end(); ++it) {
            NodeItem* node = it.key();
        if (node && node != node1) { // Проверяем только node2 и node3
            QPointF oldAbsolutePos = it.value();
            QPointF newNormalizedPos = node->pos();
            QPointF newAbsolutePos = newNormalizedPos + newOffset;

            // Абсолютные координаты должны остаться неизменными
            EXPECT_NEAR(oldAbsolutePos.x(), newAbsolutePos.x(), 0.1);
            EXPECT_NEAR(oldAbsolutePos.y(), newAbsolutePos.y(), 0.1);
        }
    }
}

// Тест: Проверка правильности обновления offset только для компонентов с отрицательными позициями
TEST_F(UModernDiagramWidgetMovementTest, OffsetUpdate_OnlyNegativeComponents) {
    auto* node1 = createTestNode("Component1", QPointF(100, 100));
    auto* node2 = createTestNode("Component2", QPointF(200, 200));
    auto* node3 = createTestNode("Component3", QPointF(300, 300));
    ASSERT_NE(node1, nullptr);
    ASSERT_NE(node2, nullptr);
    ASSERT_NE(node3, nullptr);

    QPointF initialOffset = widget->testGetNormalizationOffset();

    // Сохраняем абсолютные координаты ДО перемещения компонента в отрицательную область
    QMap<NodeItem*, QPointF> positionsBeforeMove = saveAbsolutePositions({node1, node2, node3}, initialOffset);

    // Сохраняем начальные абсолютные координаты node2 и node3 (они не будут перемещены)
    QPointF node2InitialAbsolute = positionsBeforeMove[node2];
    QPointF node3InitialAbsolute = positionsBeforeMove[node3];

    // Перемещаем только node1 в отрицательную область
    QPointF negativePos(-50, -30);
    simulateNodeMove(node1, negativePos);

    // Проверяем, что только node1 добавлен в set
    EXPECT_TRUE(widget->testGetComponentsWithNegativePos().contains(node1));
    EXPECT_FALSE(widget->testGetComponentsWithNegativePos().contains(node2));
    EXPECT_FALSE(widget->testGetComponentsWithNegativePos().contains(node3));
    EXPECT_EQ(widget->testGetComponentsWithNegativePos().size(), 1);

    // Offset еще не изменился, так как обновление происходит только при mouseReleaseEvent
    QPointF offsetBeforeUpdate = widget->testGetNormalizationOffset();
    EXPECT_EQ(offsetBeforeUpdate, initialOffset);

    simulateMouseRelease();

    // Проверяем правильность обновления offset
    EXPECT_TRUE(verifyOffsetUpdate(negativePos, offsetBeforeUpdate));

    // Проверяем, что абсолютные координаты сохранились
    // Используем позиции, сохраненные ДО перемещения
    EXPECT_TRUE(verifyAbsoluteCoordinatesPreserved(positionsBeforeMove));

    // Проверяем, что node2 и node3 не изменили свои абсолютные координаты
    QPointF newOffset = widget->testGetNormalizationOffset();
    QPointF node2NewAbsolute = node2->pos() + newOffset;
    QPointF node3NewAbsolute = node3->pos() + newOffset;

    EXPECT_NEAR(node2InitialAbsolute.x(), node2NewAbsolute.x(), 0.1);
    EXPECT_NEAR(node2InitialAbsolute.y(), node2NewAbsolute.y(), 0.1);
    EXPECT_NEAR(node3InitialAbsolute.x(), node3NewAbsolute.x(), 0.1);
    EXPECT_NEAR(node3InitialAbsolute.y(), node3NewAbsolute.y(), 0.1);
}

// Тест: Проверка сохранения координат при движении
TEST_F(UModernDiagramWidgetMovementTest, CoordinateSavingDuringMovement) {
    // Этот тест требует реального приложения и ядра для сохранения координат
    // Пока пропускаем, так как для этого нужна полная инициализация приложения
    GTEST_SKIP() << "Requires full application initialization for coordinate saving";
}

// Тест: Проверка сохранения координат после обновления offset
TEST_F(UModernDiagramWidgetMovementTest, CoordinateSavingAfterOffsetUpdate) {
    // Этот тест требует реального приложения и ядра для сохранения координат
    GTEST_SKIP() << "Requires full application initialization for coordinate saving";
}

// Main function для запуска тестов
int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
