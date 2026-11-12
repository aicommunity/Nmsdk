#include "NmsdkBuiltinKnowledgeCatalog.h"
#include "NmsdkLlmProjectContext.h"

#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <fstream>
#include <sstream>

#include <rdk_application.h>

#include "../../Libraries/Rdk-HardwareLib/Llm/RegisterHardwareLibLlmTools.h"
#include "../../Libraries/Rdk-BasicLib/Llm/RegisterBasicLibLlmTools.h"
#include "../../Libraries/Rdk-CvBasicLib/Llm/RegisterCvBasicLibLlmTools.h"
#include "../../Libraries/Nmsdk-PulseLib/Llm/RegisterPulseLibLlmTools.h"
#include "../../Libraries/Nmsdk-MotionControlLib/Llm/RegisterMotionControlLibLlmTools.h"
#include "../../Rdk/LLM/Core/Context/UDocSearchIndex.h"
#include "../../Rdk/LLM/Core/LlmPublicApi.h"

namespace fs = std::filesystem;

static fs::path detectRepositoryRoot(const std::string& work_dir)
{
    if(const char* env = std::getenv("NMSDK_ROOT"))
    {
        fs::path p(env);
        if(fs::exists(p / "CMakeLists.txt"))
            return p;
    }
    fs::path p(work_dir);
    for(int i = 0; i < 6 && p.has_parent_path(); ++i)
    {
        if(fs::exists(p / "CMakeLists.txt"))
            return p;
        p = p.parent_path();
    }
    return fs::path(work_dir);
}

NmsdkLlmProjectContext::NmsdkLlmProjectContext(RDK::UApplication* app)
    : m_app(app)
{
}

RDK::LLM::ProjectPaths NmsdkLlmProjectContext::paths() const
{
    RDK::LLM::ProjectPaths p;
    const std::string work = m_app ? m_app->GetWorkDirectory() : ".";
    p.repository_root = detectRepositoryRoot(work);
    p.bin_root = p.repository_root / "Bin";
    if(m_app && !m_app->GetClDescPath().empty())
        p.cl_desc_root = fs::path(work) / m_app->GetClDescPath();
    else
        p.cl_desc_root = p.bin_root / "ClDesc";
    if(m_app && !m_app->GetConfigsMainPath().empty())
        p.configs_root = fs::path(work) / m_app->GetConfigsMainPath();
    else
        p.configs_root = p.bin_root / "Configs";
    p.docs_root = p.repository_root / "Docs";
    return p;
}

std::vector<RDK::LLM::LibraryDescriptor> NmsdkLlmProjectContext::loadedLibraries() const
{
    return NmsdkBuiltinKnowledgeCatalog::loadedLibraries();
}

std::string NmsdkLlmProjectContext::clDescFragment(const std::string& class_name,
                                                 const std::string& locale) const
{
    const std::string key = class_name + ":" + locale;
    if(auto it = m_cldesc_cache.find(key); it != m_cldesc_cache.end())
        return it->second;

    const auto project_paths = paths();
    const auto libs = loadedLibraries();
    for(const auto& lib : libs)
    {
        const fs::path candidate =
            project_paths.cl_desc_root / lib.cl_desc_folder / locale / (class_name + ".xml");
        if(!fs::exists(candidate))
            continue;
        std::ifstream in(candidate);
        std::stringstream buffer;
        buffer << in.rdbuf();
        std::string content = buffer.str();
        if(content.size() > 32768)
        {
            const auto pos = content.find("<Properties");
            if(pos != std::string::npos)
                content = content.substr(pos, std::min<size_t>(content.size() - pos, 32768));
            else
                content.resize(32768);
        }
        m_cldesc_cache[key] = content;
        return content;
    }
    return {};
}

std::vector<RDK::LLM::DocSnippet> NmsdkLlmProjectContext::searchDocs(const std::string& query,
                                                                    int top_k,
                                                                    int) const
{
    if(RDK::LLM::LLMServices::instance().isInitialized()
       && !RDK::LLM::LLMServices::instance().searchIndex().empty())
        return RDK::LLM::LLMServices::instance().searchIndex().searchWithScope(query, top_k, "docs");

    const auto project_paths = paths();
    std::vector<fs::path> roots;
    roots.push_back(project_paths.docs_root);
    roots.push_back(project_paths.bin_root / "Docs");
    for(const auto& lib : loadedLibraries())
    {
        roots.push_back(project_paths.repository_root / "Libraries" / lib.library_id / "Docs");
    }
    return RDK::LLM::searchDocsWithIndex(roots, query, top_k);
}

void NmsdkLlmProjectContext::registerExtraTools(RDK::LLM::ULLMToolRegistry& registry,
                                              RDK::LLM::URdkDomainAccess& domain)
{
    RegisterHardwareLibLlmTools(registry, this, domain);
    RegisterBasicLibLlmTools(registry, this, domain);
    RegisterCvBasicLibLlmTools(registry, this, domain);
    RegisterPulseLibLlmTools(registry, this, domain);
    RegisterMotionControlLibLlmTools(registry, this, domain);
}
