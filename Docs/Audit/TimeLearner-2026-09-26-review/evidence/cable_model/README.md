# Модель кабеля TimeLearner (вне Console)

Повторяет явные шаги Эйлера `NPulseChannel::ACalculate2` и `NPulseSynapse::ACalculate2`
(Nmsdk-PulseLib `d52dc1c`): цепочка сегментов дендрита передаёт потенциал только от дистального
к проксимальному (`ChannelInputs`), синапс — проводимость G = p/Rs на своём сегменте.

Проверка: L=1, NSPNeuronGen (C=1e-9, Rm=1e7, DissociationTC=5 мс, 2000 Гц) даёт пик 0.0157814 —
совпадает с `InitialSomaPotential` W04 (0.015781). Подбор длин по физической синхронизации для
480 мс даёт L=[49,41,25,1] — как августовские обученные состояния.

    gcc -O2 -o cable cable.c -lm       # cable2.c: вариант с синапсом, подключённым ко всем сегментам
    python3 sweep.py 0.01 0.001 25,50,100,200    # tau=10 мс, D=1 мс: кабель, подбор L, запас
    python3 ideal_delay.py                         # идеальная задержка без дисперсии
    python3 classic_full.py 0.01 0.001 25 15,12,8,1   # полная нелинейная модель Classic
