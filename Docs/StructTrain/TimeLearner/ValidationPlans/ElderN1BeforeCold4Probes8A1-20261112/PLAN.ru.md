# Холодные физические пробы N1 before

Статус: подготовлено, runtime-приёмка ожидается. Это недостающая исходная характеристика для изолированного N1 A/B, а не само сравнение обучения.

Использовать уже собранный Elder SDK Root `5ba0a2e81759a28f378117757aa3a5b91f1c57ab` / Pulse `c10206d5e338792d42b58ab28e48e7364b07e481`. Обе source HEAD и отсутствие изменений повторно проверены native runtime snapshot. Executable SHA `ec9de2a3876a7a7e5c5e93e6715fd529ecdb7b427fe115f3eea3b31f72ddab6e`. Snapshot и его исходные байты сохранены отдельно; никаких новых сборок или изменений runtime.

Контроллер зафиксирован на общем `fd55a9936ba6018ca86e583c0e844b10fb582d56`, предусмотренном прежним matched A/B scope. Production public CLI создаёт свежую штатную N4 модель для каждого из четырёх входов Classic/Branch и наблюдает её реакцию на исходную пачку при2000Гц. Всего8 проб; target, threshold100, Rs86M, storage physics и исходные допуски сохранены. Graph/actual stimuli/полные3601 samples и validity проверяются штатными audits. Приёмка1 Python case с8 реальными Console probes не называется8 обучениями или успешной классификацией.

Результат должен пройти полную проверку source/runtime/fixture closure, закрытия outer и всех child groups, освобождения lease. После этого сравнить исходные графы и waveform с ранее принятой after characterization на том же Elder; допускаются различия provenance, связанные с объявленным SDK subject. Не использовать after observations под before runtime identity.

Следующий самостоятельный gate — холодное обучение обеих версий на одинаковых условиях с явным search budget, анализом посещённых geometry/Rs и свежих измеренных residuals. Он ещё не запущен и не закрывается этими пробами. При необходимости сначала выполнять Classic pair, публиковать сжатые primary, затем Branch pair: на Elder при подготовке свободно2334732288 bytes. Предел текущего output512MiB, минимальный free1GiB; предыдущее after SDK и все данные сохраняются.
