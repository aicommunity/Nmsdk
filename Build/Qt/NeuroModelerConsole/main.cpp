#include <QCoreApplication>
#include <iostream>
#include "../../../Rdk/Deploy/Include/rdk_cpp_initlib.h"
#include "../../../Rdk/Core/Application/UApplication.h"
#include <boost/program_options/cmdline.hpp>
#include <boost/program_options/variables_map.hpp>
#include <boost/program_options/options_description.hpp>
#include <boost/program_options/parsers.hpp>
#include "../../../Rdk/GUI/Qt/UEngineControlQt.h"

using namespace std;

namespace po = boost::program_options;

po::options_description CmdLineDescription("Allowed options");
po::variables_map CmdVariablesMap;

std::string Version("0.7.0");
//std::map<std::string,std::string> ParsedArgs;

/// �������� ��������� �������� ������
RDK::URpcDecoderInternal RdkRpcDecoder;

/// �������� ������ ���������� ������
RDK::URpcDispatcher RdkRpcDispatcher;

/// �������� ������ ����������
RDK::UApplication RdkApplication;

/// ��������� ������ ����������� �������
RDK::UServerControl RdkServerControl;
RDK::URpcDecoderCommon RdkRpcDecoderCommon;

/// ��������� ������ ����������� �������
UEngineControlQt RdkEngineControl;

/// �������� ������ �������
RDK::UProject RdkProject;

int ParseArgs(int argc, char* argv[], std::map<std::string,std::string> &parsed_args)
{
 if(argc<0 || argc>100)
  return 9000001;

 parsed_args["Application"]=argv[0];
 int index=1;
 for(int i=1;i<argc-1;i++)
 {
  parsed_args[argv[i]]=argv[i+1];
  index+=2;
 }

 return RDK_SUCCESS;
}

int RdkApplicationInit(const std::string &application_name)
{
 RdkApplication.SetApplicationFileName(application_name);
 // ������ ��������� ����������
 std::string opt_name=RDK::extract_file_name(application_name);
 if(opt_name.size()>4)
  opt_name=opt_name.substr(0,opt_name.size()-4);
 std::string app_path=RDK::extract_file_path(application_name);
 RdkApplication.SetWorkDirectory(app_path);

 RdkRpcDispatcher.SetDecoderPrototype(&RdkRpcDecoder);
 RdkRpcDispatcher.SetCommonDecoder(&RdkRpcDecoderCommon);
 RdkApplication.SetRpcDispatcher(&RdkRpcDispatcher);
 RdkApplication.SetServerControl(&RdkServerControl);
 RdkApplication.SetEngineControl(&RdkEngineControl);
 RdkApplication.SetProject(&RdkProject);
// RdkApplication.SetLogDir("EventsLog/");
 RdkApplication.SetDebugMode(true);
 RdkApplication.SetDebugMode(false);
 if(!RdkApplication.Init())
  return 9000010;
 return RDK_SUCCESS;
}

void InitCmdParser(void)
{
 CmdLineDescription.add_options()
    ("help", "produce help message")
    ("conf", po::value<string>(), "Configuration file name")
    ("ctime", po::value<double>(), "Calculation time interval, in seconds")
    ("info", po::value<string>(), "Information about core, possible: CollectionsList, ClassesList, CollectionClassesList, ClassProperties")
    ("class", po::value<string>(), "Class name")
    ("collection", po::value<string>(), "collection name")
    ("mask", po::value<unsigned>(), "Property mask")
    ("save_model_bmp", po::value<string>(), "Component name")
    ("session", po::value<unsigned>(), "Session Id")
;
}

int main(int argc, char* argv[])
{
 QCoreApplication a(argc, argv);

 InitCmdParser();

 po::store(po::parse_command_line(argc, argv, CmdLineDescription), CmdVariablesMap);
 po::notify(CmdVariablesMap);

 if (CmdVariablesMap.count("help"))
 {
  cout << CmdLineDescription << "\n";
  return 1;
 }

 int res(RDK_SUCCESS);

 cout << "NMSDK console version "<<Version<<endl;

 std::string configuration_name;
 res=RdkApplicationInit(argv[0]);
 if(res != RDK_SUCCESS)
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
 bool open_res=RdkApplication.OpenProject(configuration_name);
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


 RdkApplication.StartChannel(0);
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
 RdkApplication.PauseChannel(0);
 RDK::Sleep(100);
 MCore_ChannelUnInit(0);
 return a.exec();
}
