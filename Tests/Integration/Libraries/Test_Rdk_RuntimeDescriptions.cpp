#include <gtest/gtest.h>
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Rdk/Core/Engine/ULibrary.h"
#include "../../../Rdk/Core/System/rdk_system.h"
#include <chrono>
#include <condition_variable>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <system_error>
#include <thread>
#include <vector>
#include <stdexcept>

namespace {
class RuntimeLibraryView : public RDK::URuntimeLibrary {
public:
    explicit RuntimeLibraryView(const std::filesystem::path& path)
        : URuntimeLibrary("DescriptionFixture", "1.0", path.string()) {}
    const std::vector<std::string>& Descriptions() const { return ClassesStructures; }
};

std::filesystem::path MakeDescriptions(const std::string& suffix)
{
    const char* output = std::getenv("TIMELEARNER_EXECUTION_OUTPUT");
    const auto path = output ? std::filesystem::path(std::string(output)+".descriptions-"+suffix)
        : std::filesystem::temp_directory_path()/("nmsdk-descriptions-"+suffix+"-"+
            std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
    if(!std::filesystem::create_directory(path))throw std::runtime_error("description_fixture_already_exists");
    for(int i=0;i<32;++i) {
        std::ofstream file(path/("description-"+std::to_string(i)+".xml"),std::ios::binary);
        file<<"<ClassDescription><ClassName>Fixture"<<i<<"</ClassName></ClassDescription>";
        if(!file)throw std::runtime_error("description_fixture_write_failed");
    }
    return path;
}

void CheckOrderedDescriptions(const std::filesystem::path& path)
{
    std::vector<std::string> files;
    ASSERT_EQ(0,RDK::FindFilesList(path.string(),"*.xml",true,files));
    ASSERT_EQ(32u,files.size());
    std::vector<std::string> expected;
    for(const auto& file:files) {
        RDK::USerStorageXML xml;
        ASSERT_TRUE(xml.LoadFromFile((path/file).string(),""));
        std::string serialized;xml.Save(serialized);expected.push_back(serialized);
    }
    RuntimeLibraryView library(path);
    ASSERT_NO_THROW(ASSERT_TRUE(library.LoadCompDescriptions()));
    EXPECT_EQ(expected,library.Descriptions());
}

// This guard is used only after checking a private, kernel-enforced <=32-task
// group. Its waiting threads are released before the capture handshake.
struct OccupiedSlots {
    std::mutex mutex;
    std::condition_variable condition;
    bool released=false;
    std::vector<std::thread> threads;
    ~OccupiedSlots() {
        {std::lock_guard<std::mutex> lock(mutex);released=true;}
        condition.notify_all();
        for(auto& thread:threads)thread.join();
    }
    bool Fill() {
        for(int i=0;i<64;++i) {
            try {
                threads.emplace_back([this] {
                    std::unique_lock<std::mutex> lock(mutex);
                    condition.wait(lock,[this]{return released;});
                });
            } catch(const std::system_error& error) {
                return error.code().default_error_condition()==std::errc::resource_unavailable_try_again;
            }
        }
        return false;
    }
};
}

TEST(RuntimeDescriptions, PreservesNativeFileOrderAndSerializedContent)
{
    CheckOrderedDescriptions(MakeDescriptions("ordered"));
}

TEST(RuntimeDescriptions, LoadsWhenOwnBoundedGroupHasNoSpareThreadSlots)
{
#ifdef __linux__
    std::ifstream groups("/proc/self/cgroup");std::string line,relative;
    while(std::getline(groups,line))if(line.rfind("0::",0)==0)relative=line.substr(3);
    ASSERT_FALSE(relative.empty());
    auto group=std::filesystem::path("/sys/fs/cgroup")/std::filesystem::path(relative).relative_path();
    bool bounded=false;
    for(;group!="/sys/fs/cgroup" && group.has_parent_path();group=group.parent_path()) {
        std::ifstream stream(group/"pids.max");std::string maximum;stream>>maximum;
        if(!maximum.empty() && maximum!="max") {
            const auto limit=std::stoul(maximum);
            if(limit>=8 && limit<=32)bounded=true;
        }
    }
    if(!bounded)GTEST_SKIP()<<"Requires the explicit <=32-task contained metadata resource gate";
    const auto path=MakeDescriptions("bounded");
    OccupiedSlots slots;ASSERT_TRUE(slots.Fill());ASSERT_FALSE(slots.threads.empty());
    CheckOrderedDescriptions(path);
#else
    GTEST_SKIP()<<"The bounded resource fault is a Linux cgroup fixture";
#endif
}
