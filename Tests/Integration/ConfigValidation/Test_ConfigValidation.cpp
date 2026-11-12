#include <iostream>
#include <string>
#include <vector>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <filesystem>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#include <sys/wait.h>
#endif

namespace fs = std::filesystem;

struct TestCase {
    std::string name;
    std::string configPath;
    int expectedExitCode;
    std::vector<std::string> expectedErrorPatterns;
    std::vector<std::string> expectedWarningPatterns;
};

// Получаем путь к исполняемому файлу NeuroModelerConsole
std::string getNeuroModelerConsolePath() {
#ifdef NEUROMODELER_CONSOLE_EXE
    return std::string(NEUROMODELER_CONSOLE_EXE);
#else
    // Попытка найти исполняемый файл
    std::vector<std::string> possiblePaths = {
        "Bin/Platform/Linux/NeuroModelerConsole",
        "Bin/Platform/Windows/NeuroModelerConsole.exe",
        "../Bin/Platform/Linux/NeuroModelerConsole",
        "../Bin/Platform/Windows/NeuroModelerConsole.exe"
    };
    
    for (const auto& path : possiblePaths) {
        if (fs::exists(path)) {
            return fs::absolute(path).string();
        }
    }
    
    return "NeuroModelerConsole"; // Попытка найти в PATH
#endif
}

// Получаем путь к тестовым конфигурациям
std::string getTestConfigsDir() {
#ifdef TEST_CONFIGS_DIR
    return std::string(TEST_CONFIGS_DIR);
#else
    return "Bin/Configs/TestValidation";
#endif
}

// Выполняет команду и возвращает результат
struct CommandResult {
    int exitCode;
    std::string stdoutOutput;
    std::string stderrOutput;
};

CommandResult executeCommand(const std::string& command) {
    CommandResult result;
    
#ifdef _WIN32
    // Windows реализация
    HANDLE hChildStd_OUT_Rd = NULL;
    HANDLE hChildStd_OUT_Wr = NULL;
    HANDLE hChildStd_ERR_Rd = NULL;
    HANDLE hChildStd_ERR_Wr = NULL;
    
    SECURITY_ATTRIBUTES saAttr;
    saAttr.nLength = sizeof(SECURITY_ATTRIBUTES);
    saAttr.bInheritHandle = TRUE;
    saAttr.lpSecurityDescriptor = NULL;
    
    if (!CreatePipe(&hChildStd_OUT_Rd, &hChildStd_OUT_Wr, &saAttr, 0)) {
        result.exitCode = -1;
        return result;
    }
    if (!SetHandleInformation(hChildStd_OUT_Rd, HANDLE_FLAG_INHERIT, 0)) {
        result.exitCode = -1;
        return result;
    }
    
    if (!CreatePipe(&hChildStd_ERR_Rd, &hChildStd_ERR_Wr, &saAttr, 0)) {
        result.exitCode = -1;
        return result;
    }
    if (!SetHandleInformation(hChildStd_ERR_Rd, HANDLE_FLAG_INHERIT, 0)) {
        result.exitCode = -1;
        return result;
    }
    
    PROCESS_INFORMATION piProcInfo;
    STARTUPINFOA siStartInfo;
    ZeroMemory(&piProcInfo, sizeof(PROCESS_INFORMATION));
    ZeroMemory(&siStartInfo, sizeof(STARTUPINFOA));
    siStartInfo.cb = sizeof(STARTUPINFOA);
    siStartInfo.hStdError = hChildStd_ERR_Wr;
    siStartInfo.hStdOutput = hChildStd_OUT_Wr;
    siStartInfo.dwFlags |= STARTF_USESTDHANDLES;
    
    if (!CreateProcessA(NULL, const_cast<char*>(command.c_str()), NULL, NULL, TRUE, 0, NULL, NULL, &siStartInfo, &piProcInfo)) {
        result.exitCode = -1;
        return result;
    }
    
    CloseHandle(hChildStd_OUT_Wr);
    CloseHandle(hChildStd_ERR_Wr);
    
    DWORD dwRead;
    CHAR chBuf[4096];
    std::string stdoutStr, stderrStr;
    
    while (true) {
        if (!ReadFile(hChildStd_OUT_Rd, chBuf, 4096, &dwRead, NULL) || dwRead == 0) break;
        stdoutStr.append(chBuf, dwRead);
    }
    
    while (true) {
        if (!ReadFile(hChildStd_ERR_Rd, chBuf, 4096, &dwRead, NULL) || dwRead == 0) break;
        stderrStr.append(chBuf, dwRead);
    }
    
    WaitForSingleObject(piProcInfo.hProcess, INFINITE);
    DWORD exitCode;
    GetExitCodeProcess(piProcInfo.hProcess, &exitCode);
    result.exitCode = exitCode;
    
    CloseHandle(piProcInfo.hProcess);
    CloseHandle(piProcInfo.hThread);
    CloseHandle(hChildStd_OUT_Rd);
    CloseHandle(hChildStd_ERR_Rd);
    
    result.stdoutOutput = stdoutStr;
    result.stderrOutput = stderrStr;
#else
    // Linux реализация
    int pipe_stdout[2], pipe_stderr[2];
    if (pipe(pipe_stdout) == -1 || pipe(pipe_stderr) == -1) {
        result.exitCode = -1;
        return result;
    }
    
    pid_t pid = fork();
    if (pid == 0) {
        // Дочерний процесс
        close(pipe_stdout[0]);
        close(pipe_stderr[0]);
        dup2(pipe_stdout[1], STDOUT_FILENO);
        dup2(pipe_stderr[1], STDERR_FILENO);
        close(pipe_stdout[1]);
        close(pipe_stderr[1]);
        
        execl("/bin/sh", "sh", "-c", command.c_str(), nullptr);
        exit(127);
    } else if (pid > 0) {
        // Родительский процесс
        close(pipe_stdout[1]);
        close(pipe_stderr[1]);
        
        char buffer[4096];
        ssize_t n;
        while ((n = read(pipe_stdout[0], buffer, sizeof(buffer) - 1)) > 0) {
            buffer[n] = '\0';
            result.stdoutOutput += buffer;
        }
        while ((n = read(pipe_stderr[0], buffer, sizeof(buffer) - 1)) > 0) {
            buffer[n] = '\0';
            result.stderrOutput += buffer;
        }
        
        close(pipe_stdout[0]);
        close(pipe_stderr[0]);
        
        int status;
        waitpid(pid, &status, 0);
        result.exitCode = WEXITSTATUS(status);
    } else {
        result.exitCode = -1;
        return result;
    }
#endif
    
    return result;
}

// Проверяет, содержит ли строка паттерн
bool containsPattern(const std::string& text, const std::string& pattern) {
    return text.find(pattern) != std::string::npos;
}

// Проверяет тестовый случай
bool runTestCase(const TestCase& testCase, const std::string& consoleExe, const std::string& configsDir) {
    std::cout << "\n=== Тест: " << testCase.name << " ===" << std::endl;
    
    std::string configPath = configsDir + "/" + testCase.configPath;
    
    if (!fs::exists(configPath)) {
        std::cerr << "ОШИБКА: Файл конфигурации не найден: " << configPath << std::endl;
        return false;
    }
    
    std::string command = "\"" + consoleExe + "\" --check-config \"" + fs::absolute(configPath).string() + "\"";
    std::cout << "Команда: " << command << std::endl;
    
    CommandResult result = executeCommand(command);
    
    std::cout << "Exit code: " << result.exitCode << " (ожидалось: " << testCase.expectedExitCode << ")" << std::endl;
    
    bool passed = true;
    
    // Проверка exit code
    if (result.exitCode != testCase.expectedExitCode) {
        std::cerr << "ОШИБКА: Неправильный exit code!" << std::endl;
        passed = false;
    }
    
    // Проверка паттернов ошибок
    for (const auto& pattern : testCase.expectedErrorPatterns) {
        if (!containsPattern(result.stdoutOutput + result.stderrOutput, pattern)) {
            std::cerr << "ОШИБКА: Ожидаемый паттерн ошибки не найден: " << pattern << std::endl;
            passed = false;
        } else {
            std::cout << "  ✓ Найден паттерн ошибки: " << pattern << std::endl;
        }
    }
    
    // Проверка паттернов предупреждений
    for (const auto& pattern : testCase.expectedWarningPatterns) {
        if (!containsPattern(result.stdoutOutput + result.stderrOutput, pattern)) {
            std::cerr << "ОШИБКА: Ожидаемый паттерн предупреждения не найден: " << pattern << std::endl;
            passed = false;
        } else {
            std::cout << "  ✓ Найден паттерн предупреждения: " << pattern << std::endl;
        }
    }
    
    if (passed) {
        std::cout << "✓ Тест пройден" << std::endl;
    } else {
        std::cout << "✗ Тест провален" << std::endl;
        std::cout << "STDOUT:\n" << result.stdoutOutput << std::endl;
        std::cout << "STDERR:\n" << result.stderrOutput << std::endl;
    }
    
    return passed;
}

int main(int argc, char* argv[]) {
    std::cout << "=== Интеграционные тесты валидации конфигураций ===" << std::endl;
    
    std::string consoleExe = getNeuroModelerConsolePath();
    std::string configsDir = getTestConfigsDir();
    
    std::cout << "NeuroModelerConsole: " << consoleExe << std::endl;
    std::cout << "Тестовые конфигурации: " << configsDir << std::endl;
    
    if (!fs::exists(consoleExe)) {
        std::cerr << "ОШИБКА: NeuroModelerConsole не найден: " << consoleExe << std::endl;
        return 1;
    }
    
    if (!fs::exists(configsDir)) {
        std::cerr << "ОШИБКА: Директория с тестовыми конфигурациями не найдена: " << configsDir << std::endl;
        return 1;
    }
    
    // Определяем тестовые случаи
    std::vector<TestCase> testCases = {
        {
            "Валидная конфигурация",
            "test_valid/project.ini",
            2,
            {"Configuration is VALID"},
            {}
        },
        {
            "Отсутствующий файл модели",
            "test_missing_model/project.ini",
            1,
            {"Can't open model file"},
            {}
        },
        {
            "Отсутствующий файл параметров",
            "test_missing_parameters/project.ini",
            2,
            {"Configuration is VALID"},
            {}
        },
        {
            "Невалидный XML",
            "test_invalid_xml/project.ini",
            1,
            {"Configuration is INVALID"},
            {}
        },
        {
            "Пустая модель",
            "test_empty_model/project.ini",
            1,
            {"Configuration is INVALID"},
            {"Model is empty"}
        },
        {
            "Несуществующие классы компонентов",
            "test_invalid_classes/project.ini",
            1,
            {"Configuration is INVALID"},
            {}
        },
        {
            "Неправильные связи",
            "test_invalid_links/project.ini",
            2,
            {"Configuration is VALID"},
            {}
        }
    };
    
    int passed = 0;
    int failed = 0;
    
    for (const auto& testCase : testCases) {
        if (runTestCase(testCase, consoleExe, configsDir)) {
            passed++;
        } else {
            failed++;
        }
    }
    
    std::cout << "\n=== Итоги ===" << std::endl;
    std::cout << "Пройдено: " << passed << std::endl;
    std::cout << "Провалено: " << failed << std::endl;
    std::cout << "Всего: " << (passed + failed) << std::endl;
    
    return failed > 0 ? 1 : 0;
}
