> Исторический startup. Задание завершено; [принятый результат](RESULT.ru.md).

# Bundle-only replay на Elder запущен

Job `s11-recorded-matrix-portable1-elder-a1`, source/controller `f1d1953da0dff6b3b0636c433dbea16c65b9d49c`. Supervisor PID200327, actual main PID203397, unit `timelearner-855052a1-13ff-4734-89ac-7fc3567cdd05.service`, invocation `3e2b615e9350413c93b5402ff651ff17`, kernel active/running.

Единственный fixture binding — шесть файлов published compact bundle из Git commit `7e8483ca7ffad8ca211edd57ed9070568e4dfd29`, fingerprint `730cabfee0a332c2fd58dd6077d9f4281c9cf3100e7524d2c3c00aa30dfd0fac`. Исходные M40 source/run directories не передавались. Код вызывает production bounded restore и scorer; true native execution/learning/scientific PASS не заявляются. Source+data+request доставлены Git packs, без rsync/scp.

Лимиты4GiB/32tasks/14400s, output1GiB, minimum free512MiB. По timeout наблюдателя не перезапускать: сначала проверить unit/binding, worker terminal и controller-result. Actual test приёмка ещё ожидается.
