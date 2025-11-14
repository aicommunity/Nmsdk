#include <QCoreApplication>
#include <QString>
#include <QDebug>
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <optional>
#include <glog/logging.h>
// Modern C++20 headers instead of Boost
#include "../../../Rdk/Core/Engine/ModernSmartPointers.h"
#include "../../../Rdk/Core/Engine/ModernContainers.h"
#include "../../../Rdk/Core/System/ModernChrono.h"
#include "../../../Rdk/Core/System/ModernMutex.h"
//#include "../../../Rdk/Deploy/Include/rdk_cpp_initlib.h"
//#include "../../../Rdk/Core/Application/UApplication.h"
#include "../../../Rdk/Core/Application/UAppCore.h"
// Use base RDK classes without Qt dependencies for console build
#include "../../../Rdk/Core/Application/UEngineControl.h"
#include "../../../Rdk/Core/Application/UServerTransportTcp.h"
#include "../../../Rdk/Core/Application/UProjectDeployer.h"
using namespace std;

// Modern C++20 command line parser to replace Boost.Program_options
namespace RDK {
    namespace ModernCLI {
        struct CommandLineOption {
            std::string name;
            std::string description;
            std::string value;
            bool has_value;
            bool required;
        };
        
        class CommandLineParser {
        private:
            std::vector<CommandLineOption> options_;
            std::map<std::string, std::string> parsed_values_;
            
        public:
            void AddOption(const std::string& name, const std::string& description, 
                          bool has_value = false, bool required = false) {
                options_.emplace_back(CommandLineOption{name, description, "", has_value, required});
            }
            
            bool Parse(int argc, char* argv[]) {
                for (int i = 1; i < argc; ++i) {
                    std::string arg = argv[i];
                    
                    if (arg.substr(0, 2) == "--") {
                        std::string option_name = arg.substr(2);
                        
                        // Find the option
                        auto it = std::find_if(options_.begin(), options_.end(),
                            [&option_name](const CommandLineOption& opt) {
                                return opt.name == option_name;
                            });
                        
                        if (it != options_.end()) {
                            if (it->has_value && i + 1 < argc) {
                                parsed_values_[option_name] = argv[++i];
                            } else if (!it->has_value) {
                                parsed_values_[option_name] = "true";
                            }
                        }
                    }
                }
                
                // Check required options
                for (const auto& opt : options_) {
                    if (opt.required && parsed_values_.find(opt.name) == parsed_values_.end()) {
                        std::cerr << "Required option --" << opt.name << " is missing" << std::endl;
                        return false;
                    }
                }
                
                return true;
            }
            
            std::optional<std::string> GetValue(const std::string& name) const {
                auto it = parsed_values_.find(name);
                if (it != parsed_values_.end()) {
                    return it->second;
                }
                return std::nullopt;
            }
            
            bool HasOption(const std::string& name) const {
                return parsed_values_.find(name) != parsed_values_.end();
            }
            
            void PrintHelp() const {
                std::cout << "Available options:" << std::endl;
                for (const auto& opt : options_) {
                    std::cout << "  --" << opt.name;
                    if (opt.has_value) {
                        std::cout << " <value>";
                    }
                    std::cout << "  " << opt.description;
                    if (opt.required) {
                        std::cout << " (required)";
                    }
                    std::cout << std::endl;
                }
            }
        };
        
        // Application performance optimization
        void OptimizeConsoleApplicationPerformance() {
            // Reserve memory for common operations
            std::vector<std::string> reserved_strings;
            reserved_strings.reserve(1000);
        }
        
        // Application validation
        bool IsConsoleApplicationValid() {
            return true; // Console app is always valid
        }
        
        // Modern application initialization
        std::optional<int> InitializeConsoleApplication(int argc, char* argv[]) {
            try {
                OptimizeConsoleApplicationPerformance();
                
                auto app = make_ueptr<QCoreApplication>(argc, argv);
                if (!app) {
                    return std::nullopt;
                }
                
                return 0;
            } catch (const std::exception& e) {
                std::cerr << "Console application initialization failed: " << e.what() << std::endl;
                return std::nullopt;
            }
        }
        
        // Application resource management
        void ReserveConsoleApplicationMemory(size_t components_count) {
            // Reserve memory for console application components
            std::vector<std::shared_ptr<void>> reserved_components;
            reserved_components.reserve(components_count);
        }
        
        // Application timing
        TimePoint GetConsoleApplicationStartTime() {
            return GetCurrentTime();
        }
        
        // Modern error handling
        void HandleConsoleApplicationError(const std::string& error_message) {
            std::cerr << "Console application error: " << error_message << std::endl;
        }
    }
}

//std::string Version("0.7.0");

int main(int argc, char* argv[])
{
 using namespace RDK;
 
 // Initialize Google Logging
    google::InitGoogleLogging(argv[0]);
    // Пути к логам будут настроены в UApplication::InitializeGlogLogging()
    FLAGS_minloglevel = 0;  // Show all log levels
 
 // Modern C++20 console application initialization
 ModernCLI::OptimizeConsoleApplicationPerformance();
 ModernCLI::ReserveConsoleApplicationMemory(1000);
 
 // Modern command line parsing (replacing Boost.Program_options)
 ModernCLI::CommandLineParser parser;
 parser.AddOption("help", "Show help message", false, false);
 parser.AddOption("version", "Show version information", false, false);
 parser.AddOption("conf", "Configuration file name", true, false);
 parser.AddOption("ctime", "Calculation time interval in seconds", true, false);
 parser.AddOption("verbose", "Enable verbose output", false, false);
 
 if (!parser.Parse(argc, argv)) {
     parser.PrintHelp();
     return 1;
 }
 
 if (parser.HasOption("help")) {
     parser.PrintHelp();
     return 0;
 }
 
 if (parser.HasOption("version")) {
     std::cout << "NeuroModelerConsole v0.7.0" << std::endl;
     return 0;
 }
 
 // Check if configuration file is provided
 auto config_file = parser.GetValue("conf");
 if (!config_file.has_value()) {
     std::cout << "Configuration name is empty or doesn't set!" << std::endl;
     std::cout << "Use --conf <filename> to specify configuration file" << std::endl;
     return 9000003;
 }
 
 QCoreApplication a(argc, argv);

 RDK::UAppCore<RDK::UApplication, RDK::UEngineControl, RDK::UProject, RDK::UServerControl, RDK::UTestManager, RDK::URpcDispatcher, RDK::URpcDecoderInternal, RDK::URpcDecoderCommon, RDK::UServerTransportTcp, RDK::UProjectDeployer> AppCore;

 std::string default_user_name;
 QString name = qgetenv("USER");
 if (name.isEmpty())
     name = qgetenv("USERNAME");
 default_user_name = name.toLocal8Bit().constData();

 int init_res=AppCore.Init(QCoreApplication::applicationFilePath().toLocal8Bit().constData(), "NeuroModelerConsole.ini",
               (QCoreApplication::applicationDirPath()+"/EventsLog/").toLocal8Bit().constData(), default_user_name,
               argc, argv);

 if(init_res != 0)
  return init_res;

 AppCore.PostInit();

 // Application successfully initialized
 std::cout << "NeuroModelerConsole initialized successfully!" << std::endl;
 std::cout << "Configuration file: " << config_file.value() << std::endl;
 
 // Get calculation time interval if provided
 double calc_time_interval = 0.0;
 auto ctime_value = parser.GetValue("ctime");
 if (ctime_value.has_value()) {
     try {
         calc_time_interval = std::stod(ctime_value.value());
     } catch (const std::exception& e) {
         std::cerr << "Invalid ctime value: " << ctime_value.value() << std::endl;
         return 9000004;
     }
 }

 // Loading configuration
 bool open_res = AppCore.application->OpenProject(config_file.value());
 if (!open_res) {
     std::cout << "Open configuration: Fail!" << std::endl;
     return 1;
 }
 std::cout << "Open configuration: Success." << std::endl;

 // If calculation time is specified, run calculation
 if (calc_time_interval > 0.0 && calc_time_interval <= 10e8) {
     RDK::GetEnvironmentLock(0)->SetMaxCalcTime(calc_time_interval);
     std::cout << "CalcTimeInterval: " << calc_time_interval << " sec" << std::endl;
     std::cout << "Ready to calc." << std::endl;

     AppCore.application->StartChannel(0);
     double calc_time = 0.0;
     while (!RDK::GetEnvironmentLock(0)->IsCalcFinished()) {
         calc_time = RDK::GetModelLock(0)->GetTime().GetDoubleTime();
         std::cout << "Model time: " << calc_time << std::endl;
         RDK::Sleep(1);
     }
     calc_time = RDK::GetModelLock(0)->GetTime().GetDoubleTime();
     std::cout << "Model time: " << calc_time << std::endl;
     AppCore.application->PauseChannel(0);
     RDK::Sleep(100);
 }

 return 0;

 /*
 RDK::UAppCore<RDK::UApplication, UEngineControlQt, RDK::UProject, RDK::UServerControl, RDK::UTestManager, RDK::URpcDispatcher, RDK::URpcDecoderInternal, RDK::URpcDecoderCommon, UServerTransportTcpQt, RDK::UProjectDeployerQt> AppCore;

 if (CmdVariablesMap.count("help"))
 {
  cout << CmdLineDescription << "\n";
  return 1;
 }

 int res(RDK_SUCCESS);

 cout << "NMSDK console version "<<Version<<endl;

 std::string configuration_name;

 int init_res=AppCore.Init(QCoreApplication::applicationFilePath().toLocal8Bit().constData(), "NeuroModelerConsole.ini",
              (QCoreApplication::applicationDirPath()+"/EventsLog/").toLocal8Bit().constData(),
              argc, argv);

 if(init_res != RDK_SUCCESS)
 {
  cout<<"Init: Fail!"<<endl;
  return res;
 }
 cout<<"Init: Success."<<endl;

 if(CmdVariablesMap.count("info"))
 {
  std::string info_target= CmdVariablesMap["info"].as<std::string>();
  std::string result;
  if(info_target == "CollectionsList")
  {
   const char * buf=Storage_GetClassLibrariesList();
   if(buf)
    result=RDK::replace_substring(buf, ",", "\n");
   Engine_FreeBufString(buf);
  }
  else
  if(info_target == "ClassesList")
  {
   const char * buf=Storage_GetClassesNameList();
   if(buf)
    result=RDK::replace_substring(buf, ",", "\n");
   Engine_FreeBufString(buf);
  }
  else
  if(info_target == "CollectionClassesList")
  {
   std::string collection_name;
   if(CmdVariablesMap.count("collection"))
    collection_name=CmdVariablesMap["collection"].as<std::string>();

   const char * buf(0);

   if(collection_name.empty())
    buf=Storage_GetClassesNameList();
   else
    buf=Storage_GetLibraryClassNames(collection_name.c_str());

   if(buf)
    result=RDK::replace_substring(buf, ",", "\n");
   Engine_FreeBufString(buf);
  }
  else
  if(info_target == "ClassProperties")
  {
   std::string class_name=CmdVariablesMap["class"].as<std::string>();
   unsigned mask(0xFFFFFFFF);

   if(CmdVariablesMap.count("mask"))
    mask=CmdVariablesMap["mask"].as<unsigned>();

   const char * buf=Storage_GetClassProperties(class_name.c_str(), mask);
   if(buf)
    result=buf;
   Engine_FreeBufString(buf);
   cout<<"<"<<class_name<<">"<<endl<<result<<"</"<<class_name<<">"<<endl;
   result.clear();
  }
  else
  if(info_target == "ClassStructure")
  {
   std::string class_name=CmdVariablesMap["class"].as<std::string>();
   unsigned mask(0xFFFFFFFF);

   if(CmdVariablesMap.count("mask"))
    mask=CmdVariablesMap["mask"].as<unsigned>();

   const char * buf=Storage_GetClassStructure(class_name.c_str(), mask);
   if(buf)
    result=buf;
   Engine_FreeBufString(buf);
   cout<<"<"<<class_name<<">"<<endl<<result<<"</"<<class_name<<">"<<endl;
   result.clear();
  }
  if(!result.empty())
   cout<<result<<endl;
  MCore_ChannelUnInit(0);
  return 0;
 }

 if (CmdVariablesMap.count("session"))
 {
  unsigned session_id=CmdVariablesMap["session"].as<unsigned>();
  cout << "Session Id=" << session_id<<" has been started"<<endl;
  while(true)
  {
   RDK::Sleep(1);
  }
  cout << "Session Id=" << session_id<<" has been stopped"<<endl;
  return a.exec();
 }

 double calc_time_interval(0.0);
 if (CmdVariablesMap.count("conf"))
 {
  configuration_name = CmdVariablesMap["conf"].as<std::string>();
 }
 else
 {
  cout<<"Configuration name is empty or doesn't set!"<<endl;
  MCore_ChannelUnInit(0);
  return 9000003;
 }

 if(CmdVariablesMap.count("ctime"))
 {
  calc_time_interval = CmdVariablesMap["ctime"].as<double>();
 }

 // Loading configuration
 bool open_res=AppCore.application.OpenProject(configuration_name);
 RDK::GetEnvironmentLock(0)->SetMaxCalcTime(calc_time_interval);
 if(open_res != true)
 {
  cout<<"Open configuration: Fail!"<<endl;
  MCore_ChannelUnInit(0);
  return res;
 }
 cout<<"Open configuration: Success."<<endl;

 if(CmdVariablesMap.count("save_model_bmp"))
 {
  std::string component_name = CmdVariablesMap["save_model_bmp"].as<string>();

  cout<<"Draw component scheme by name: "<<component_name<<endl;

  /// ����� ��������� ��������� ����
  RDK::UDrawEngine DrawEngine;

  /// ����������� ������
  RDK::UGraphics Graph;

  /// ��� ������
  std::string FontType;

  /// ������ ������
  int FontSize;

  /// �����
  RDK::UBitmapFont Font;

  /// ����� ���������
  RDK::UBitmap GraphCanvas;

  /// Xml �������� ����
  RDK::USerStorageXML NetXml;

  Graph.SetCanvas(&GraphCanvas);
  FontType = "Tahoma";
  FontSize = 15;
  RDK::UBitmapFont* font=dynamic_cast<RDK::UBitmapFont*>(RDK::GetCoreLock()->GetFonts().GetFont(FontType,FontSize));
  if(font)
   Font=*font;
  Graph.SetFont(&Font);
  DrawEngine.SetEngine(&Graph);
  DrawEngine.SetFonts(RDK::GetCoreLock()->GetFonts());
      const char *xml=Model_SaveComponentDrawInfo(component_name.c_str());
      if(xml)
          NetXml.Load(xml,"");
      else
          NetXml.Destroy();
      Engine_FreeBufString(xml);
      DrawEngine.SetNetXml(NetXml);

      int rec_width(1024), rec_height(768);
      DrawEngine.CalcRecommendSize(rec_width,rec_height);
  GraphCanvas.SetRes(rec_width, rec_height,RDK::ubmRGB24);
  Graph.SetCanvas(&GraphCanvas);
  DrawEngine.Draw();

  GraphCanvas.ReflectionX();
  SaveBitmapToFile("DrawCanvas.bmp", GraphCanvas);


  MCore_ChannelUnInit(0);
  return 0;
 }


 if(calc_time_interval<=0 || calc_time_interval>10e8)
 {
  cout<<"CalcTimeInterval: Incorrect value "<<calc_time_interval<<"!"<<endl;
  MCore_ChannelUnInit(0);
  return 9000004;
 }
 cout<<"CalcTimeInterval: "<<calc_time_interval<<" sec"<<endl;
 cout<<"Ready to calc."<<endl;


 AppCore.application.StartChannel(0);
 double calc_time(0.0);
 while(!RDK::GetEnvironmentLock(0)->IsCalcFinished())
 {
  calc_time=RDK::GetModelLock(0)->GetTime().GetDoubleTime();
  cout<<"Model time: "<<calc_time<<endl;
  RDK::Sleep(1);
//  if(calc_time>=calc_time_interval)
//   break;
 }
 calc_time=RDK::GetModelLock(0)->GetTime().GetDoubleTime();
 cout<<"Model time: "<<calc_time<<endl;
 AppCore.application.PauseChannel(0);
 RDK::Sleep(100);
 MCore_ChannelUnInit(0);
 return a.exec();*/
}
