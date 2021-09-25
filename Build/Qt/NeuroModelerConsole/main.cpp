#include <QCoreApplication>
#include <iostream>
#include <boost/program_options/cmdline.hpp>
#include <boost/program_options/variables_map.hpp>
#include <boost/program_options/options_description.hpp>
#include <boost/program_options/parsers.hpp>
//#include "../../../Rdk/Deploy/Include/rdk_cpp_initlib.h"
//#include "../../../Rdk/Core/Application/UApplication.h"
#include "../../../Rdk/Core/Application/UAppCore.h"
#include "../../../Rdk/GUI/Qt/UEngineControlQt.h"
#include "../../../Rdk/Core/Application/Qt/UProjectDeployerQt.h"
#include "../../../Rdk/Core/Application/Qt/UServerTransportTcpQt.h"
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

 RDK::UAppCore<RDK::UApplication, UEngineControlQt, RDK::UProject, RDK::UServerControl, RDK::UTestManager, RDK::URpcDispatcher, RDK::URpcDecoderInternal, RDK::URpcDecoderCommon, UServerTransportTcpQt, RDK::UProjectDeployerQt> AppCore;

 int init_res=AppCore.Init(QCoreApplication::applicationFilePath().toLocal8Bit().constData(), "NeuroModelerConsole.ini",
               (QCoreApplication::applicationDirPath()+"/EventsLog/").toLocal8Bit().constData(),
               argc, argv);

 if(init_res != 0)
  return init_res;

 AppCore.PostInit();

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

  /// Класс рисования структуры сети
  RDK::UDrawEngine DrawEngine;

  /// Графический движок
  RDK::UGraphics Graph;

  /// Тип шрифта
  std::string FontType;

  /// Размер шрифта
  int FontSize;

  /// Шрифт
  RDK::UBitmapFont Font;

  /// Канва рисования
  RDK::UBitmap GraphCanvas;

  /// Xml описание сети
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
