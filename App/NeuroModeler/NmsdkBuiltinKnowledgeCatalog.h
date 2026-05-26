#ifndef NMSDK_BUILTIN_KNOWLEDGE_CATALOG_H
#define NMSDK_BUILTIN_KNOWLEDGE_CATALOG_H

#include "../../Rdk/LLM/Core/Context/ILLMKnowledgeCatalog.h"
#include "../../Rdk/LLM/Core/Context/ILLMProjectContextProvider.h"

namespace RDK {
class UApplication;
}

class NmsdkBuiltinKnowledgeCatalog : public RDK::LLM::ILLMKnowledgeCatalog {
public:
    explicit NmsdkBuiltinKnowledgeCatalog(RDK::UApplication* app);

    std::vector<RDK::LLM::LLMKnowledgeSource> sources() const override;
    std::filesystem::path prebuiltIndexDirectory() const override;
    std::string catalogFingerprint() const override;

    /// Single source for ClDesc folders (TD-039); synced with Libraries.cpp.
    static std::vector<RDK::LLM::LibraryDescriptor> loadedLibraries();
    /// Write `Docs/llms.txt` for external LLM crawlers (TD-032).
    bool writeLlmsTxt(const std::filesystem::path& repository_root) const;

private:
    std::filesystem::path m_repository_root;
};

#endif
