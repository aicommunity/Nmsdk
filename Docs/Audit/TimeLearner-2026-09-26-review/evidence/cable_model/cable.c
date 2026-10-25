// Branch/Classic cascade simulator replicating NPulseChannel/NPulseSynapse Euler updates.
// usage: cable f C Rm Rs tdiss tsec tpulse T nstages nsyn  [syn_pos:pulse_times;...]
// Simpler API: reads from stdin lines: nstages; then nsyn lines "pos Rs ntimes t1 t2 ..."; prints soma deviation trace subsampled.
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
int main(int argc,char**argv){
  double f=atof(argv[1]),C=atof(argv[2]),Rm=atof(argv[3]),td=atof(argv[4]),ts=atof(argv[5]),tp=atof(argv[6]),T=atof(argv[7]);
  int sub=atoi(argv[8]); int jacobi=argc>9?atoi(argv[9]):0;
  int n; if(scanf("%d",&n)!=1) return 1; // n segments (dendrite), stage index 0..n-1 = segment n..1 (distal->proximal), stage n = soma
  int ns; scanf("%d",&ns);
  int *pos=malloc(sizeof(int)*ns); double *Rs=malloc(sizeof(double)*ns); int *nt=malloc(sizeof(int)*ns); double **tt=malloc(sizeof(double*)*ns);
  for(int i=0;i<ns;i++){scanf("%d %lf %d",&pos[i],&Rs[i],&nt[i]); tt[i]=malloc(sizeof(double)*(nt[i]+1)); for(int j=0;j<nt[i];j++) scanf("%lf",&tt[i][j]);}
  int S=n+1; double *V=malloc(sizeof(double)*S),*Vo=malloc(sizeof(double)*S),*G=calloc(S,sizeof(double));
  double *p=calloc(ns,sizeof(double)); int *cnt=calloc(ns,sizeof(int)); int *nx=calloc(ns,sizeof(int));
  for(int i=0;i<S;i++) V[i]=-1;
  long steps=(long)(T*f); int pc=(int)(tp*f);
  for(long k=0;k<steps;k++){
    double t=k/f;
    for(int i=0;i<S;i++) G[i]=0;
    for(int i=0;i<ns;i++){
      while(nx[i]<nt[i] && tt[i][nx[i]]<=t+1e-12){cnt[i]=pc; nx[i]++;}
      if(cnt[i]>0){p[i]+=(1-p[i])/(ts*f); cnt[i]--;} else p[i]-=p[i]/(td*f);
      int stage=n-pos[i]; // segment pos (1..n) -> stage index
      G[stage]+=p[i]/Rs[i];
    }
    if(jacobi) for(int i=0;i<S;i++) Vo[i]=V[i];
    for(int i=0;i<S;i++){
      double inp = (i==0)? -1.0 : (jacobi?Vo[i-1]:V[i-1]);
      double g=G[i]; double Ti=C/(g+1.0/Rm); double su=1+g*Rm;
      V[i]+=(inp-V[i]*su)/(Ti*f);
    }
    if(k%sub==0) printf("%.9g\n",V[S-1]+1.0);
  }
  return 0;
}
