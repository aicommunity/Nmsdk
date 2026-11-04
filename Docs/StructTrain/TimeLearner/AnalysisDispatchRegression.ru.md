# Регрессия CLI analyze из-за локального импорта

На actual native304 source8021301e plain analyze падал с UnboundLocalError:
main содержит условный `from matched_resistance_analysis import analyze`;
Python делает analyze локальным именем во всей main. Поэтому обычный dispatcher
не мог вызвать верхнеуровневую analyze(args), даже если matched-ветка не выбрана.
Та же коллизия есть в принятом root8b231dae9. Этот дефект не является отказом
C++ обучения;18 subtest failures и два отдельных inventory errors не смешиваются.

Исправление: импорт matched-функции с явным именем analyze_matched_resistance.
Оба call sites обращаются к правильным функциям. Форматы, статусы, научные
допуски, data parser и математическая цель не меняются. Существующая suite
AnalysisCliTest из5 actual-native checks покрывает positive domain, unknown
schema, output collision, mandatory probe trace и historical schema adapter.
До реальных server checks runtime acceptance остаётся pending.

Отдельные ошибки границ inventory schema3/schema4 и ModelSpec2 в joint reader119
не исправляются ослаблением подсчёта; им нужен декларативный набор по actual
native spec. CLI hotfix не утверждает приёмку совместного C-search среза.
