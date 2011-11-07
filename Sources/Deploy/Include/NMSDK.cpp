#ifndef NMSDK_CPP
#define NMSDK_CPP

#include "nmsdk.h"
#include "../../Kernel/NKernel.cpp"
#include "../../Libraries/NLibraries.cpp"
#include "../../GUI/NGraphics.cpp"


namespace NMSDK {

// ������� ������ ��������� � ���������� ��������� �� ����
RDK::UAContainerStorage* NewNStorage(void)
{
 return new NStorage;
}

// ������� ����� � ���������� ��������� �� ���
RDK::UAContainerEnvironment* NewNEnvironment(void)
{
 NEnvironment *env=new NEnvironment;

 env->AddClassLibrary(&BCLLibrary);
 env->AddClassLibrary(&ActLibrary);
 env->AddClassLibrary(&CRLibrary);
 env->AddClassLibrary(&MathLibrary);
 env->AddClassLibrary(&PhysLibrary);
 env->AddClassLibrary(&SensorLibrary);
 env->AddClassLibrary(&SourceLibrary);
 env->AddClassLibrary(&ReceiverLibrary);
 env->AddClassLibrary(&PulseLibrary);
 env->AddClassLibrary(&NeuronLifeLibrary);
 env->AddClassLibrary(&PulseNeuronLibrary);
 env->AddClassLibrary(&MotionControlLibrary);
 return env;
}

}
#endif
