#include <QCoreApplication>
#include <QCommandLineParser>
#include <QTimer>
#include <QDir>
#include <QString>
#include <QDebug>
#include <iostream>
#include <algorithm>
#include <utility>
#include <vector>
#include <boost/program_options/cmdline.hpp>
#include <boost/program_options/variables_map.hpp>
#include <boost/program_options/options_description.hpp>
#include <boost/program_options/parsers.hpp>
#include "ClDescGenerator.h"
#include "../../../Rdk/Deploy/Include/rdk_cpp_initdll.h"
#include "../../../Rdk/Core/Application/UAppCore.h"
// Use base RDK classes without Qt dependencies for console build
#include "../../../Rdk/Core/Application/UEngineControl.h"
#include "../../../Rdk/Core/Application/UServerTransportTcp.h"
#include "../../../Rdk/Core/Application/UProjectDeployer.h"
using namespace std;

//namespace po = boost::program_options;
//namespace RDK {

//extern po::options_description CmdLineDescription;
//extern po::variables_map CmdVariablesMap;

//}

//std::string Version("0.7.0");

int main(int argc, char* argv[])
{
 using namespace RDK;
 QCoreApplication a(argc, argv);

 QCommandLineParser parser;
 parser.setApplicationDescription("NeuroModelerConsole automation arguments");
 parser.addHelpOption();
 const QCommandLineOption configOption(QStringList() << "c" << "config",
                                       "Path to project ini to open.",
                                       "path");
 const QCommandLineOption startCalcOption(QStringList() << "s" << "start-calc",
                                          "Start calculations immediately after launch.");
 const QCommandLineOption calcTimeOption(QStringList() << "t" << "calc-time",
                                         "Calculation time interval in seconds.",
                                         "seconds");
const QCommandLineOption exitAfterOption(QStringList() << "x" << "exit-after-calc",
                                         "Exit application after calculations finish.");
const QCommandLineOption generateClDescOption(QStringList() << "g" << "generate-cldesc",
                                              "Generate XML descriptions for loaded component classes and exit.");
const QCommandLineOption lexiconOption(QStringList() << "l" << "cldesc-lexicon",
                                       "Optional path to custom lexicon JSON used during description generation.",
                                       "path");
const QCommandLineOption clDescLibraryOption(QStringList() << "C" << "cldesc-library",
                                             "Limit generation to the specified library name (can be repeated).",
                                             "name");
const QCommandLineOption clDescClassOption(QStringList() << "K" << "cldesc-class",
                                           "Limit generation to the specified component class name (can be repeated).",
                                           "class");
const QCommandLineOption clDescForceOption(QStringList() << "F" << "cldesc-force",
                                           "Force overwrite of existing headers/descriptions when generating ClDesc.");
const QCommandLineOption checkConfigOption(QStringList() << "check-config" << "validate-config",
                                          "Validate configuration file and exit with error code.",
                                          "path");
parser.addOption(configOption);
parser.addOption(startCalcOption);
parser.addOption(calcTimeOption);
parser.addOption(exitAfterOption);
parser.addOption(generateClDescOption);
parser.addOption(lexiconOption);
parser.addOption(clDescLibraryOption);
parser.addOption(clDescClassOption);
parser.addOption(clDescForceOption);
parser.addOption(checkConfigOption);
 parser.process(a);

 auto buildForwardArgs = [&parser]() {
  QStringList original = QCoreApplication::arguments();
  std::vector<std::string> storage;
  storage.reserve(original.size());
  std::vector<char*> pointers;

  auto push_arg = [&](const QString& value) {
   storage.emplace_back(value.toLocal8Bit().constData());
   pointers.push_back(storage.back().data());
  };

  if(!original.isEmpty())
   push_arg(original.front());

 auto shouldSkipValue = [](const QString& option) {
  return option == "--config" || option == "-c" ||
         option == "--calc-time" || option == "-t" ||
         option == "--cldesc-lexicon" || option == "-l" ||
         option == "--cldesc-library" || option == "-C" ||
         option == "--cldesc-class" || option == "-K" ||
         option == "--check-config" || option == "--validate-config";
  };

  for(int i=1; i<original.size(); ++i)
  {
   const QString token = original[i];
   if(token == "--config" || token == "-c" ||
      token == "--start-calc" || token == "-s" ||
      token == "--calc-time" || token == "-t" ||
      token == "--exit-after-calc" || token == "-x" ||
      token == "--generate-cldesc" || token == "-g" ||
      token == "--cldesc-lexicon" || token == "-l" ||
      token == "--cldesc-library" || token == "-C" ||
      token == "--cldesc-class" || token == "-K" ||
      token == "--check-config" || token == "--validate-config")
   {
    if(shouldSkipValue(token) && i + 1 < original.size())
     ++i;
    continue;
   }
   push_arg(token);
  }

  return std::pair<std::vector<std::string>, std::vector<char*>>{std::move(storage), std::move(pointers)};
 };

 auto [forwardStorage, forwardPointers] = buildForwardArgs();
 int forwardedArgc = static_cast<int>(forwardPointers.size());
 char** forwardedArgv = forwardPointers.data();

 const QString cliConfigPath = parser.value(configOption).trimmed();
 const bool cliStartCalc = parser.isSet(startCalcOption);
 const bool cliExitAfterCalc = parser.isSet(exitAfterOption);
const bool cliGenerateClDesc = parser.isSet(generateClDescOption);
const QString cliCheckConfig = parser.value(checkConfigOption).trimmed();
const QString cliLexiconPath = parser.value(lexiconOption).trimmed();
const QStringList cliLibraryFilters = parser.values(clDescLibraryOption);
const QStringList cliClassFilters = parser.values(clDescClassOption);
 double cliCalcTimeSec = 0.0;
 if(parser.isSet(calcTimeOption))
 {
  bool ok=false;
  const double parsed = parser.value(calcTimeOption).toDouble(&ok);
  if(ok && parsed > 0.0)
   cliCalcTimeSec = parsed;
 }

 RDK::UAppCore<RDK::UApplication, RDK::UEngineControl, RDK::UProject, RDK::UServerControl, RDK::UTestManager, RDK::URpcDispatcher, RDK::URpcDecoderInternal, RDK::URpcDecoderCommon, RDK::UServerTransportTcp, RDK::UProjectDeployer> AppCore;

 std::string default_user_name;
 QString name = qgetenv("USER");
 if (name.isEmpty())
     name = qgetenv("USERNAME");
 default_user_name = name.toLocal8Bit().constData();

 int init_res=AppCore.Init(QCoreApplication::applicationFilePath().toLocal8Bit().constData(), "NeuroModelerConsole.ini",
               (QCoreApplication::applicationDirPath()+"/EventsLog/").toLocal8Bit().constData(), default_user_name,
               forwardedArgc, forwardedArgv);

 if(init_res != 0)
  return init_res;

 // Обработка проверки конфигурации
 if(!cliCheckConfig.isEmpty())
 {
  QString configPath = cliCheckConfig;
  if(configPath.isEmpty() && !cliConfigPath.isEmpty())
  {
   configPath = cliConfigPath;
  }
  
  if(configPath.isEmpty())
  {
   qCritical() << "Error: Configuration file path is required for --check-config";
   return 1;
  }

  RDK::TProjectLoadDiagnostics diagnostics = AppCore.application.ValidateProject(configPath.toLocal8Bit().constData());
  
  // Выводим результаты
  std::cout << "Configuration validation results:" << std::endl;
  std::cout << "  Model exists: " << (diagnostics.modelExists ? "Yes" : "No") << std::endl;
  std::cout << "  Model empty: " << (diagnostics.modelEmpty ? "Yes" : "No") << std::endl;
  
  if(!diagnostics.componentsCount.empty())
  {
   std::cout << "  Components count per channel:";
   for(size_t i = 0; i < diagnostics.componentsCount.size(); ++i)
   {
	std::cout << " [" << i << "]=" << diagnostics.componentsCount[i];
   }
   std::cout << std::endl;
  }
  
  std::cout << "  Channels loaded: " << diagnostics.channelsLoaded << "/" << diagnostics.channelsTotal << std::endl;
  std::cout << "  Errors: " << diagnostics.errors.size() << std::endl;
  std::cout << "  Warnings: " << diagnostics.warnings.size() << std::endl;
  
  if(!diagnostics.errors.empty())
  {
   std::cerr << std::endl << "Errors:" << std::endl;
   for(const std::string& error : diagnostics.errors)
   {
	std::cerr << "  - " << error << std::endl;
   }
  }
  
  if(!diagnostics.warnings.empty())
  {
   std::cout << std::endl << "Warnings:" << std::endl;
   for(const std::string& warning : diagnostics.warnings)
   {
	std::cout << "  - " << warning << std::endl;
   }
  }
  
  if(!diagnostics.missingFiles.empty())
  {
   std::cerr << std::endl << "Missing files:" << std::endl;
   for(const std::string& file : diagnostics.missingFiles)
   {
	std::cerr << "  - " << file << std::endl;
   }
  }
  
  if(!diagnostics.failedChannels.empty())
  {
   std::cerr << std::endl << "Failed channels:";
   for(int channel : diagnostics.failedChannels)
   {
	std::cerr << " " << channel;
   }
   std::cerr << std::endl;
  }
  
  std::cout << std::endl << "Configuration is " << (diagnostics.isValid ? "VALID" : "INVALID") << std::endl;
  
  // Возвращаем код ошибки
  if(!diagnostics.isValid || !diagnostics.errors.empty())
  {
   return 1; // Есть ошибки
  }
  else if(!diagnostics.warnings.empty())
  {
   return 2; // Есть только предупреждения
  }
  else
  {
   return 0; // Всё в порядке
  }
 }

 if(!cliConfigPath.isEmpty())
 {
  AppCore.startProjectName = cliConfigPath.toLocal8Bit().constData();
  AppCore.autoexecLastProjectFlag = 0;
 }
 if(cliStartCalc)
  AppCore.autoStartProjectFlag = 1;
 if(cliCalcTimeSec > 0.0)
  AppCore.calcTimeIntervalSec = cliCalcTimeSec;
 if(cliExitAfterCalc)
  AppCore.exitAfterCalcFlag = 1;

 AppCore.PostInit();

 auto configureAutomation = [&AppCore]()
 {
  if(AppCore.calcTimeIntervalSec > 0.0 && AppCore.application.GetProjectOpenFlag())
  {
   const auto& config = AppCore.application.GetProjectConfig();
   const int channel_count = std::max(1, config.NumChannels);
   for(int channel = 0; channel < channel_count; ++channel)
   {
    auto env = RDK::GetEnvironmentLock(channel);
    if(env)
     env->SetMaxCalcTime(AppCore.calcTimeIntervalSec);
   }
  }
  if(AppCore.exitAfterCalcFlag)
  {
   QTimer* monitor = new QTimer(QCoreApplication::instance());
   QObject::connect(monitor, &QTimer::timeout, [&AppCore]()
   {
    if(!AppCore.application.GetProjectOpenFlag())
     return;
    const auto& cfg = AppCore.application.GetProjectConfig();
    const int channel_count = std::max(1, cfg.NumChannels);
    for(int channel = 0; channel < channel_count; ++channel)
    {
     auto env = RDK::GetEnvironmentLock(channel);
     if(env && !env->IsCalcFinished())
      return;
    }
    QCoreApplication::quit();
   });
   monitor->start(500);
  }
 };

 configureAutomation();

if(cliGenerateClDesc)
{
 auto storageLock = RDK::GetStorageLock();
 if(!storageLock)
 {
  qCritical() << "Не удалось получить доступ к UStorage для генерации описаний.";
  return 2;
 }

 const QString workspaceRoot = QDir(QCoreApplication::applicationDirPath()).absoluteFilePath(QStringLiteral("../../../"));
 const QString clDescPath = QDir(workspaceRoot).absoluteFilePath(QStringLiteral("Bin/ClDesc/"));
 const QString libsPath = QDir(workspaceRoot).absoluteFilePath(QStringLiteral("Bin/RTlibs/"));
 QDir().mkpath(clDescPath);

 AppCore.application.SetClDescPath(clDescPath.toStdString());
 AppCore.application.SetLibrariesPath(libsPath.toStdString());

 if(auto coreLock = RDK::GetCoreLock())
 {
  coreLock->SetClDescPath(clDescPath.toStdString());
  coreLock->SetLibrariesPath(libsPath.toStdString());
 }
 storageLock->SetClDescPath(clDescPath.toStdString());

 NeuroModeler::ClDescGenerator generator;
 NeuroModeler::ClDescGeneratorOptions options;
 if(!cliLexiconPath.isEmpty())
  options.lexiconCandidatePaths << cliLexiconPath;
 const QString defaultLexiconPath = QDir(workspaceRoot).absoluteFilePath(QStringLiteral("Docs/ClDescLexicon.json"));
 options.lexiconCandidatePaths << defaultLexiconPath
                               << QStringLiteral("Docs/ClDescLexicon.json");
 if(!cliLibraryFilters.isEmpty())
  options.libraryFilters = cliLibraryFilters;
if(!cliClassFilters.isEmpty())
 options.classFilters = cliClassFilters;
 options.verbose = true;
// В этом режиме всегда принудительно обновляем заголовки и описания,
// опираясь на словарь и автогенерацию.
options.forceOverride = true;

 QString errorMessage;
 if(!generator.Generate(storageLock, options, &errorMessage))
 {
  if(!errorMessage.isEmpty())
   qCritical() << errorMessage;
  return 2;
 }

 qInfo() << "Генерация описаний классов успешно завершена.";
 return 0;
}

 return a.exec();

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
