#include "NmsdkBuiltinKnowledgeCatalog.h"

#include <cstdlib>
#include <sstream>

#include <rdk_application.h>

namespace {

using RDK::LLM::LLMKnowledgeKind;
using RDK::LLM::LLMKnowledgeSource;

LLMKnowledgeSource makeSource(const char* source_id, const std::filesystem::path& root,
                              LLMKnowledgeKind kind,
                              std::initializer_list<const char*> extensions,
                              std::initializer_list<const char*> excludes = {})
{
    LLMKnowledgeSource source;
    source.source_id = source_id;
    source.root = root;
    source.kind = kind;
    for(const char* ext : extensions)
        source.extensions.emplace_back(ext);
    for(const char* pattern : excludes)
        source.exclude_globs.emplace_back(pattern);
    return source;
}

std::filesystem::path detectRepositoryRoot(const std::string& work_dir)
{
    if(const char* env = std::getenv("NMSDK_ROOT"))
    {
        const std::filesystem::path p(env);
        if(std::filesystem::exists(p / "CMakeLists.txt"))
            return p;
    }
    std::filesystem::path p(work_dir);
    for(int i = 0; i < 6 && p.has_parent_path(); ++i)
    {
        if(std::filesystem::exists(p / "CMakeLists.txt"))
            return p;
        p = p.parent_path();
    }
    return std::filesystem::path(work_dir);
}

} // namespace

NmsdkBuiltinKnowledgeCatalog::NmsdkBuiltinKnowledgeCatalog(RDK::UApplication* app)
{
    const std::string work = app ? app->GetWorkDirectory() : ".";
    m_repository_root = detectRepositoryRoot(work);
}

std::vector<LLMKnowledgeSource> NmsdkBuiltinKnowledgeCatalog::sources() const
{
    const auto root = [&](const char* rel) { return m_repository_root / rel; };

    std::vector<LLMKnowledgeSource> out;
    auto add = [&](LLMKnowledgeSource source) {
        if(std::filesystem::exists(source.root))
            out.push_back(std::move(source));
    };

    add(makeSource("nmsdk.app", root("App/NeuroModeler"), LLMKnowledgeKind::AppSource,
                   {".cpp", ".h"}));
    add(makeSource("nmsdk.app.console", root("App/NeuroModelerConsole"), LLMKnowledgeKind::AppSource,
                   {".cpp", ".h"}));

    {
        LLMKnowledgeSource loader =
            makeSource("nmsdk.libraries.loader", root("Libraries"), LLMKnowledgeKind::LibrarySource,
                       {".cpp", ".h"});
        loader.include_files_only = {"Libraries.cpp", "Libraries.h"};
        add(std::move(loader));
    }

    add(makeSource("rdk.core", root("Rdk/Core"), LLMKnowledgeKind::RdkSource,
                   {".cpp", ".h", ".hpp"}, {"Console/**"}));
    add(makeSource("rdk.deploy.api", root("Rdk/Deploy/Include"), LLMKnowledgeKind::RdkSource,
                   {".h", ".cpp"}));
    add(makeSource("rdk.gui.qt", root("Rdk/GUI/Qt"), LLMKnowledgeKind::RdkSource,
                   {".cpp", ".h", ".hpp", ".ui"}, {"static/**", "**/moc_*.cpp"}));
    add(makeSource("rdk.llm", root("Rdk/LLM"), LLMKnowledgeKind::RdkSource, {".cpp", ".h"},
                   {"Docs/**", "Tests/**"}));

    add(makeSource("lib.basic", root("Libraries/Rdk-BasicLib/Core"), LLMKnowledgeKind::LibrarySource,
                   {".cpp", ".h"}));
    add(makeSource("lib.basic.gui", root("Libraries/Rdk-BasicLib/GUI/Qt"),
                   LLMKnowledgeKind::LibrarySource, {".cpp", ".h"}));
    add(makeSource("lib.cvbasic", root("Libraries/Rdk-CvBasicLib/Core"), LLMKnowledgeKind::LibrarySource,
                   {".cpp", ".h"}));
    add(makeSource("lib.cvbasic.gui", root("Libraries/Rdk-CvBasicLib/GUI/Qt"),
                   LLMKnowledgeKind::LibrarySource, {".cpp", ".h"}));
    add(makeSource("lib.hardware", root("Libraries/Rdk-HardwareLib/Core"),
                   LLMKnowledgeKind::LibrarySource, {".cpp", ".h"}));
    add(makeSource("lib.hardware.gui", root("Libraries/Rdk-HardwareLib/GUI/Qt"),
                   LLMKnowledgeKind::LibrarySource, {".cpp", ".h"}));
    add(makeSource("lib.pulse", root("Libraries/Nmsdk-PulseLib/Core"), LLMKnowledgeKind::LibrarySource,
                   {".cpp", ".h"}));
    add(makeSource("lib.pulse.gui", root("Libraries/Nmsdk-PulseLib/GUI/Qt"),
                   LLMKnowledgeKind::LibrarySource, {".cpp", ".h"}));
    add(makeSource("lib.motion", root("Libraries/Nmsdk-MotionControlLib/Core"),
                   LLMKnowledgeKind::LibrarySource, {".cpp", ".h"}));
    add(makeSource("lib.motion.gui", root("Libraries/Nmsdk-MotionControlLib/GUI/Qt"),
                   LLMKnowledgeKind::LibrarySource, {".cpp", ".h"}));

    add(makeSource("lib.hardware.llm", root("Libraries/Rdk-HardwareLib/Llm"),
                   LLMKnowledgeKind::LibraryDocs, {".cpp", ".h", ".md"}));
    add(makeSource("lib.pulse.llm", root("Libraries/Nmsdk-PulseLib/Llm"), LLMKnowledgeKind::LibraryDocs,
                   {".cpp", ".h", ".md"}));
    add(makeSource("lib.motion.llm", root("Libraries/Nmsdk-MotionControlLib/Llm"),
                   LLMKnowledgeKind::LibraryDocs, {".cpp", ".h", ".md"}));
    add(makeSource("lib.basic.llm", root("Libraries/Rdk-BasicLib/Llm"), LLMKnowledgeKind::LibraryDocs,
                   {".cpp", ".h", ".md"}));
    add(makeSource("lib.cvbasic.llm", root("Libraries/Rdk-CvBasicLib/Llm"), LLMKnowledgeKind::LibraryDocs,
                   {".cpp", ".h", ".md"}));

    add(makeSource("nmsdk.docs", root("Docs"), LLMKnowledgeKind::ProductDocs, {".md"}));
    add(makeSource("rdk.docs", root("Rdk/Docs"), LLMKnowledgeKind::RdkCoreDocs, {".md"}));
    add(makeSource("rdk.llm.docs", root("Rdk/LLM/Docs"), LLMKnowledgeKind::RdkCoreDocs, {".md"}));
    add(makeSource("lib.basic.docs", root("Libraries/Rdk-BasicLib/Docs"), LLMKnowledgeKind::LibraryDocs,
                   {".md"}));
    add(makeSource("lib.cvbasic.docs", root("Libraries/Rdk-CvBasicLib/Docs"), LLMKnowledgeKind::LibraryDocs,
                   {".md"}));
    add(makeSource("lib.hardware.docs", root("Libraries/Rdk-HardwareLib/Docs"),
                   LLMKnowledgeKind::LibraryDocs, {".md"}));
    add(makeSource("lib.pulse.docs", root("Libraries/Nmsdk-PulseLib/Docs"), LLMKnowledgeKind::LibraryDocs,
                   {".md"}));
    add(makeSource("lib.motion.docs", root("Libraries/Nmsdk-MotionControlLib/Docs"),
                   LLMKnowledgeKind::LibraryDocs, {".md"}));
    add(makeSource("bin.docs", root("Bin/Docs"), LLMKnowledgeKind::BinDocs, {".md"}));

    return out;
}

std::filesystem::path NmsdkBuiltinKnowledgeCatalog::prebuiltIndexDirectory() const
{
    return m_repository_root / "Bin/LLM/index";
}

std::string NmsdkBuiltinKnowledgeCatalog::catalogFingerprint() const
{
    std::ostringstream oss;
    for(const LLMKnowledgeSource& source : sources())
        oss << source.source_id << '|' << source.root.string() << '\n';
    const std::size_t h = std::hash<std::string>{}(oss.str());
    std::ostringstream hex;
    hex << std::hex << h;
    std::string fp = hex.str();
    if(fp.size() > 16)
        fp.resize(16);
    return fp;
}
