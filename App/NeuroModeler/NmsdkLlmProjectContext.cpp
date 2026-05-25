#include "NmsdkLlmProjectContext.h"

#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <fstream>
#include <sstream>

#include <rdk_application.h>

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
    return {{"Rdk-BasicLib", "BasicLibrary"},
            {"Rdk-CvBasicLib", "CvBasicLibrary"},
            {"Rdk-HardwareLib", "HardwareLibrary"},
            {"Nmsdk-PulseLib", "PulseLibrary"},
            {"Nmsdk-MotionControlLib", "MotionControlLibrary"}};
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
    std::vector<RDK::LLM::DocSnippet> out;
    const auto project_paths = paths();
    std::vector<fs::path> roots;
    roots.push_back(project_paths.docs_root);
    roots.push_back(project_paths.bin_root / "Docs");
    for(const auto& lib : loadedLibraries())
    {
        roots.push_back(project_paths.repository_root / "Libraries" / lib.library_id / "Docs");
    }

    const std::string qlower = [&]() {
        std::string s = query;
        std::transform(s.begin(), s.end(), s.begin(),
                       [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
        return s;
    }();

    auto consider = [&](const fs::path& file) {
        if(!file.has_extension() || (file.extension() != ".md" && file.extension() != ".txt"))
            return;
        std::ifstream in(file);
        std::string line;
        std::string excerpt;
        while(std::getline(in, line) && excerpt.size() < 400)
            excerpt += line + "\n";
        std::string lower = excerpt;
        std::transform(lower.begin(), lower.end(), lower.begin(),
                       [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
        if(lower.find(qlower) == std::string::npos && file.filename().string().find(query) ==
                                                         std::string::npos)
            return;
        RDK::LLM::DocSnippet sn;
        sn.path = file.string();
        sn.title = file.filename().string();
        sn.excerpt = excerpt.substr(0, 400);
        sn.score = 0.5;
        out.push_back(std::move(sn));
    };

    for(const fs::path& root : roots)
    {
        if(!fs::exists(root))
            continue;
        for(auto it = fs::recursive_directory_iterator(root);
            it != fs::recursive_directory_iterator(); ++it)
        {
            if(it->is_regular_file())
                consider(it->path());
            if(static_cast<int>(out.size()) >= top_k)
                break;
        }
        if(static_cast<int>(out.size()) >= top_k)
            break;
    }
    return out;
}
