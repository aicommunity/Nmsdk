// NOTE: parameter f everywhere = integration steps per second (NMSDK DefaultTimeStep), dt = 1/f. It is NOT a spike rate.
// Faithful-ish NMSDK single-dendrite (Branch) segment neuron, one input channel.
// Gauss-Seidel distal->proximal update as NPulseChannel::ACalculate2 (see cable_model/cable.c),
// exc chain (rest -1) + inh chain (rest +1), soma LTZ = Ve_soma + Vi_soma, threshold with
// soma feedback (gain FG, R->FBR while |Feedback|>1e-3), multi-trial with ITI.
// stdin: n ns ; then ns lines "pos type(1 exc,-1 inh) Rs" ; then ntr ; then per trial "k t1..tk" (trial-relative, s)
// args: f Ce Rme Ci Rmi FBR theta FG td ts tp ITI Twin mode
// mode 0: per trial print "peak tpeak start nspk" ; mode 1: print trace of LTZ potential (every 10 steps)
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
int main(int argc,char**argv){
  double f=atof(argv[1]),Ce=atof(argv[2]),Rme=atof(argv[3]),Ci=atof(argv[4]),Rmi=atof(argv[5]),FBR=atof(argv[6]);
  double th=atof(argv[7]),FG=atof(argv[8]),td=atof(argv[9]),ts=atof(argv[10]),tp=atof(argv[11]),ITI=atof(argv[12]),Tw=atof(argv[13]);
  int mode=atoi(argv[14]);
  int n,ns; if(scanf("%d %d",&n,&ns)!=2) return 1;
  int *pos=malloc(ns*sizeof(int)),*typ=malloc(ns*sizeof(int)); double *Rs=malloc(ns*sizeof(double));
  for(int i=0;i<ns;i++) scanf("%d %d %lf",&pos[i],&typ[i],&Rs[i]);
  int ntr; scanf("%d",&ntr); int *nk=malloc(ntr*sizeof(int)); double **tt=malloc(ntr*sizeof(double*));
  for(int r=0;r<ntr;r++){scanf("%d",&nk[r]); tt[r]=malloc((nk[r]+1)*sizeof(double)); for(int j=0;j<nk[r];j++) scanf("%lf",&tt[r][j]);}
  int S=n+1; double *Ve=malloc(S*sizeof(double)),*Vi=malloc(S*sizeof(double)),*Ge=calloc(S,sizeof(double)),*Gi=calloc(S,sizeof(double));
  for(int i=0;i<S;i++){Ve[i]=-1;Vi[i]=1;}
  double p=0; int cnt=0; int pc=(int)llround(tp*f); if(pc<1)pc=1;
  double TT=Tw+ITI; long per=(long)llround(TT*f); double fb=0; int pulse=0;
  for(int r=0;r<ntr;r++){
    int nx=0; double pk=-1e9,tpk=0,start=0; int nsp=0;
    for(long k=0;k<per;k++){
      double t=k/f;
      while(nx<nk[r] && tt[r][nx]<=t+1e-12){cnt=pc;nx++;}
      if(cnt>0){p+=(1-p)/(ts*f);cnt--;} else p-=p/(td*f);
      for(int i=0;i<S;i++){Ge[i]=0;Gi[i]=0;}
      for(int i=0;i<ns;i++){int st=n-pos[i]; if(typ[i]>0) Ge[st]+=p/Rs[i]; else Gi[st]+=p/Rs[i];}
      for(int i=0;i<S;i++){
        double ine=(i==0)?-1.0:Ve[i-1], ini=(i==0)?1.0:Vi[i-1];
        double Re=Rme,Ri=Rmi;
        if(i==S-1 && fabs(fb)>1e-3){ine-=fb;ini-=fb;Re=FBR;Ri=FBR;}
        double Ti=Ce/(Ge[i]+1.0/Re), su=1+Ge[i]*Re; Ve[i]+=(ine-Ve[i]*su)/(Ti*f);
        Ti=Ci/(Gi[i]+1.0/Ri); su=1+Gi[i]*Ri; Vi[i]+=(ini-Vi[i]*su)/(Ti*f);
      }
      double P=Ve[S-1]+Vi[S-1];
      if(k==0) start=P;
      if(P>=th){ if(!pulse){nsp++;pulse=1;} fb=FG; } else {pulse=0; fb=0;}
      if(t<=Tw && P>pk){pk=P;tpk=t;}
      if(mode==1) printf("%d %.6f %.9g\n",r,t,P);
    }
    if(mode==0) printf("%.9g %.6f %.9g %d\n",pk,tpk,start,nsp);
  }
  return 0;
}
