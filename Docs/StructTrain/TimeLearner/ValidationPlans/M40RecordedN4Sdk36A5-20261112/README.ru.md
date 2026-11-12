# A5: новый SDK после исправления opt-in configure

SDK/Tool 448b153f2fea3486ff40f3a626b8f1110b9e3ee2, Pulse7b524b8d6c760c5ecfeea432b14b5f9d5045987d. Source/build/runtime-a3 fresh; failed native-a2 не используется. Required BOOL ON явно передаётся CMake только для известной опции. Действует прежний cohort36, два больших native cases исполняются отдельно после сборки через schema5 DATA. Canonical A4 был PASS подготовки, но последующее native-a2 отказало после configure и до compile; отказ сохранён. Проверка26 включает настоящий CMake NONE cache с defaultOFF→declaredON.
