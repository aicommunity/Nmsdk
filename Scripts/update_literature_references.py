#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для массовой переработки ссылок на литературу в md файлах.
Заменяет текстовые упоминания на нумерованные ссылки [1], [2] и т.д.
"""

import re
import os
from pathlib import Path

# Словарь замен для общих паттернов (в порядке приоритета - более специфичные сначала)
replacements = [
    (r'диссертации Бахшиева А\.В\. \(2016[^)]*\)', '[A]'),
    (r'диссертация Бахшиева А\.В\. \(2016[^)]*\)', '[A]'),
    (r'Диссертация Бахшиева А\.В\. \(2016[^)]*\)', '[A]'),
    (r'Согласно диссертации Бахшиева А\.В\. \(2016[^)]*\)', 'Согласно [A]'),
    (r'ВКР Демчевой А\.А\. \(2023\)', '[2]'),
    (r'ВКР Демчевой А\.А\.', '[2]'),
    (r'Демчева А\.А\. \(2023\)', '[2]'),
    (r'ВКР Зарубина КВ', '[B]'),
    (r'ВКР Зарубина К\.В\.', '[B]'),
    (r'Зарубин К\.В\. \(2022\)', '[B]'),
    (r'Бахшиев А\.В\. \(2016\)', '[A]'),
    (r'Korsakov et al\. \(2023\)', '[1]'),
    (r'Korsakov A\.M\., Isakov T\.T\., Bakhshiev A\.V\. \(2023\)', '[1]'),
    (r'Корсаков и др\. \(2022\)', '[1]'),
    (r'Корсаков А\.М\., Астапова Л\.А\., Бахшиев А\.В\. \(2022\)', '[1]'),
    (r'Бахшиев А\.В\., Романов С\.П\.', '[31]'),  # Моделирование нейронных структур
    (r'А\.В\. Бахшиев, С\.П\. Романов', '[31]'),
    (r'Бахшиев А\.В\.', '[27]'),  # Перспективы применения
    (r'Korsakov, A\., Bakhshiev, A\.', '[13]'),  # The Neuromorphic Model
]

# Шаблоны литературы
literature_templates = {
    'cable': """## Литература

1. Bakhshiev A. V., Demcheva A. A. Compartmental spiking neuron model CSNM // Izvestiya VUZ. Applied Nonlinear Dynamics, 2022, vol. 30, iss. 3, pp. 299-310. [DOI](https://doi.org/10.18500/0869-6632-2022-30-3-299-310)

2. Демчева А.А. Разработка сегментной спайковой модели нейрона на основе кабельной теории для нейроморфных систем: выпускная квалификационная работа магистра. 2023. [онлайн](https://doi.org/10.18720/SPBPU/3/2023/vr/vr23-5657)
""",
    'stdp': """## Литература

1. Зарубин К.В. Исследование методов обучения спайковых нейронных сетей: выпускная квалификационная работа бакалавра. 2022. [онлайн](https://doi.org/10.18720/SPBPU/3/2022/vr/vr24-1435)
""",
    'rcn': """## Литература

1. Бахшиев А.В. Нейроморфные системы управления на основе модели импульсного нейрона со структурной адаптацией: диссертация на соискание ученой степени кандидата технических наук. [онлайн](https://www.elibrary.ru/item.asp?id=54445157)

2. Бахшиев А.В., Романов С.П. Моделирование нейронных структур управления мышечным сокращением. Схемы нейронных сетей. [онлайн](https://neuromodeler.ru/index.php?option=com_content&view=article&id=29:1&catid=67&lang=ru&Itemid=676)
""",
    'muscle': """## Литература

1. Бахшиев А.В. Перспективы применения моделей биологических нейронных структур в системах управления движением // Информационно-измерительные и управляющие системы: - №9, 2011. с. 71-80. [онлайн](https://www.elibrary.ru/item.asp?id=17257136)

2. Korsakov, A., Bakhshiev, A. The Neuromorphic Model of the Human Visual System // Studies in Computational Intelligence, 2021, 925 SCI, pp. 339–346. [DOI](https://link.springer.com/chapter/10.1007%2F978-3-030-60577-3_40)

3. Бахшиев А.В., Романов С.П. Моделирование нейронных структур управления мышечным сокращением. Схемы нейронных сетей. [онлайн](https://neuromodeler.ru/index.php?option=com_content&view=article&id=29:1&catid=67&lang=ru&Itemid=676)
""",
}

def detect_category(file_path):
    """Определяет категорию файла для выбора шаблона литературы"""
    path_str = str(file_path)
    if 'CableModel' in path_str or 'Cable' in path_str:
        return 'cable'
    elif 'STDP' in path_str:
        return 'stdp'
    elif 'MC0-RCN' in path_str:
        return 'rcn'
    elif 'MC-Muscles' in path_str or 'MC1-PCN' in path_str:
        return 'muscle'
    return None

def process_file(file_path):
    """Обрабатывает один файл README.md"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        has_references = False
        used_refs = set()

        # Применяем замены
        for pattern, replacement in replacements:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                has_references = True
                # Извлекаем номер ссылки
                ref_match = re.search(r'\[([0-9A-C]+)\]', replacement)
                if ref_match:
                    used_refs.add(ref_match.group(1))

        # Удаляем разделы "Связанные публикации" в начале (после заголовка)
        content = re.sub(r'### Связанные публикации\s*\n(?:\s*-\s*.*?\n)+', '', content, flags=re.MULTILINE)

        # Удаляем странные форматы с отдельными строками [номер] и ссылками
        content = re.sub(r'\n\s*\[[0-9A-C]+\]\s*\n\s*\(\[онлайн\].*?\)\s*\n', '', content)
        content = re.sub(r'\n\s*-\s*\*\*\[[0-9A-C]+\]\*\*\s*\n\s*Раздел.*?\n', '', content, flags=re.MULTILINE)

        # Удаляем разделы "### Ссылки на публикации" и заменяем на "## Литература"
        if '### Ссылки на публикации' in content:
            # Удаляем весь раздел до следующего заголовка или конца файла
            content = re.sub(r'### Ссылки на публикации.*?(?=\n##|\n###|\Z)', '', content, flags=re.DOTALL)
            has_references = True

        # Определяем категорию для выбора шаблона
        category = detect_category(file_path)

        # Добавляем литературу в конец, если её нет и есть ссылки
        if '## Литература' not in content and has_references:
            # Проверяем, есть ли ссылки в тексте
            if re.search(r'\[[0-9A-C]\]', content):
                if category and category in literature_templates:
                    content = content.rstrip() + '\n\n' + literature_templates[category]
                elif 'cable' in str(file_path).lower() or '[2]' in content:
                    # По умолчанию для CableModel
                    content = content.rstrip() + '\n\n' + literature_templates['cable']

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f'Ошибка в {file_path}: {e}')
        return False

def main():
    """Основная функция"""
    base_dir = Path('Bin/Configs/SpikeSamples')
    count = 0

    # Обрабатываем все README.md файлы
    for readme_file in base_dir.rglob('README.md'):
        if process_file(readme_file):
            count += 1
            print(f'Обработан: {readme_file}')

    print(f'Всего обработано файлов: {count}')

if __name__ == '__main__':
    main()
