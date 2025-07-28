# CI/CD Documentation

Этот проект использует GitHub Actions для автоматического тестирования на разных версиях Python и операционных системах.

## 🔄 Workflow Overview

### 1. **CI (Primary Pipeline)** - `.github/workflows/ci.yml`
Основной CI pipeline, который запускается при каждом push и pull request.

**Задачи:**
- **Lint**: Проверка кода с помощью ruff, pyright, mypy
- **Build**: Сборка пакета
- **Test**: Полное тестирование на matrix из:
  - **Python версии**: 3.8, 3.9, 3.10, 3.11, 3.12  
  - **Операционные системы**: Ubuntu, Windows, macOS
- **Docs**: Генерация документации (только Ubuntu)
- **Coverage**: Генерация отчетов покрытия кода
- **Examples**: Тестирование примеров кода с реальным API

**Особенности:**
- ✅ Кроссплатформенная установка Rye
- ✅ Отдельные команды для Windows (обход Makefile)
- ✅ Матричное тестирование: 15 комбинаций (5 Python × 3 OS)
- ✅ Условная загрузка артефактов покрытия (только Ubuntu + Python 3.12)

### 2. **Python Compatibility Check** - `.github/workflows/compatibility-check.yml`
Быстрая проверка совместимости со всеми версиями Python.

**Задачи:**
- **Compatibility Test**: Проверка импорта и базовых тестов на Python 3.8-3.12
- **Quick Install Test**: Установка через pip на всех ОС

**Особенности:**
- ⚡ Быстрый запуск (15 минут)
- 🔄 Запускается на push/PR и для develop ветки
- 📦 Тестирует установку через pip (не Rye)

### 3. **Windows Tests** - `.github/workflows/windows-test.yml`
Специализированное тестирование для Windows без Makefile.

**Задачи:**
- **Windows Test**: Прямое использование pip и pytest
- **Windows Build Test**: Тестирование сборки пакета

**Особенности:**
- 🪟 Обход проблем с Makefile на Windows
- 📅 Ежедневный запуск по расписанию (cron)
- 🧪 Прямые Python команды вместо make

### 4. **Test Status Summary** - `.github/workflows/status.yml`
Мониторинг статуса всех тестов.

**Задачи:**
- **Status Summary**: Отображение результатов всех workflow
- **Failure Notification**: Автоматическое создание issues при ошибках

**Особенности:**
- 📊 Сводный отчет по всем тестам
- 🚨 Автоматическое создание issues для main ветки
- 🔗 Ссылки на failed runs

## 📋 Test Matrix

| OS | Python Versions | Workflow | Frequency |
|---|---|---|---|
| Ubuntu | 3.8, 3.9, 3.10, 3.11, 3.12 | CI, Compatibility | Push/PR |
| Windows | 3.8, 3.9, 3.10, 3.11, 3.12 | CI, Windows Tests | Push/PR + Daily |
| macOS | 3.8, 3.9, 3.10, 3.11, 3.12 | CI | Push/PR |

**Всего комбинаций:** 15 (основной CI) + 5 (compatibility) + 5 (Windows) = **25 test jobs**

## 🚀 Triggers

### Push Events
- `main` branch: Все workflow + примеры + документация
- Feature branches: CI + Compatibility

### Pull Request Events  
- Targeting `main`: Все workflow
- Targeting `develop`: Compatibility

### Scheduled Events
- Windows Tests: Ежедневно в 02:00 UTC

## 🔧 Environment Variables

Для запуска примеров требуются secrets:
```yaml
EVOLUTION_KEY_ID: ${{ secrets.EVOLUTION_KEY_ID }}
EVOLUTION_SECRET: ${{ secrets.EVOLUTION_SECRET }}  
EVOLUTION_BASE_URL: ${{ secrets.EVOLUTION_BASE_URL }}
EVOLUTION_PROJECT_ID: ${{ secrets.EVOLUTION_PROJECT_ID }}
```

## 📊 Artifacts

- **dist/**: Собранные пакеты (.whl, .tar.gz)
- **coverage/**: Отчеты покрытия кода (HTML, XML, JSON)
- **docs/**: Сгенерированная документация

## 🛠️ Tools & Dependencies

- **Build System**: Rye (primary), pip (fallback)
- **Linting**: ruff, pyright, mypy
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Documentation**: Sphinx
- **Coverage**: coverage.py + badge generation

## 🔍 Debugging Failed Tests

1. **Check Status Summary**: Workflow status показывает общее состояние
2. **Review Logs**: Каждый job имеет детальные логи
3. **Auto Issues**: Для main ветки создаются автоматические issues
4. **Matrix Strategy**: `fail-fast: false` позволяет видеть все ошибки

## 📈 Performance Optimization

- **Parallel Jobs**: Максимальное использование GitHub Actions runners
- **Selective Runs**: 
  - Примеры только на PR/main
  - Coverage только Ubuntu + Python 3.12
  - Документация только на Linux
- **Caching**: Rye and pip dependencies cached
- **Timeouts**: Разумные timeout для каждого job

## 🏷️ Badge Status

README.md содержит бейджи для мониторинга:
- CI status
- Python compatibility  
- Windows tests
- Platform support
- Python version coverage

---

> **Примечание**: Этот CI/CD setup обеспечивает надежное тестирование на всех поддерживаемых платформах и версиях Python, гарантируя высокое качество и совместимость пакета. 