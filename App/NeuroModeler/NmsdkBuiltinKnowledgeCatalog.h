#ifndef NMSDK_BUILTIN_KNOWLEDGE_CATALOG_H
#define NMSDK_BUILTIN_KNOWLEDGE_CATALOG_H

#include "../../Rdk/LLM/Core/Context/ILLMKnowledgeCatalog.h"

namespace RDK {
class UApplication;
}

class NmsdkBuiltinKnowledgeCatalog : public RDK::LLM::ILLMKnowledgeCatalog {
public:
    explicit NmsdkBuiltinKnowledgeCatalog(RDK::UApplication* app);

    std::vector<RDK::LLM::LLMKnowledgeSource> sources() const override;
    std::filesystem::path prebuiltIndexDirectory() const override;
    std::string catalogFingerprint() const override;

private:
    std::filesystem::path m_repository_root;
};

#endif
