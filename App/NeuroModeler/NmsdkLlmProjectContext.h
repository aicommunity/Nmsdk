#ifndef NMSDK_LLM_PROJECT_CONTEXT_H
#define NMSDK_LLM_PROJECT_CONTEXT_H

#include <map>

#include "../../Rdk/LLM/Core/Context/ILLMProjectContextProvider.h"

namespace RDK {
class UApplication;
}

class NmsdkLlmProjectContext : public RDK::LLM::ILLMProjectContextProvider {
public:
    explicit NmsdkLlmProjectContext(RDK::UApplication* app);

    RDK::LLM::ProjectPaths paths() const override;
    std::vector<RDK::LLM::LibraryDescriptor> loadedLibraries() const override;
    std::string clDescFragment(const std::string& class_name,
                               const std::string& locale = "ru-RU") const override;
    std::vector<RDK::LLM::DocSnippet> searchDocs(const std::string& query, int top_k = 5,
                                                 int max_chars = 8000) const override;
    void registerExtraTools(RDK::LLM::ULLMToolRegistry& registry,
                            RDK::LLM::URdkDomainAccess& domain) override;

private:
    RDK::UApplication* m_app;
    mutable std::map<std::string, std::string> m_cldesc_cache;
};

#endif
