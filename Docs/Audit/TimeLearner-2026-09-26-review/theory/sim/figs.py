import numpy as np, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=json.load(open('../data/run_collapse.json'))
fig,ax=plt.subplots(1,2,figsize=(12,4.3))
for S,mk in ((25,'o'),(100,'s')):
    r=[x for x in R if x['S_ms']==S]; c=[x['c'] for x in r]
    ax[0].plot(c,[x['s4'] for x in r],'-'+mk,label=f'S{S}: сдвиг S/4'); ax[0].plot(c,[x['m8'] for x in r],'--'+mk,label=f'S{S}: 8 паттернов')
    ax[1].plot([x['fwhm_over_S'] for x in r],[x['s4'] for x in r],'-'+mk,label=f'S{S}')
ax[0].axhline(0.1,c='r',ls='--'); ax[0].axvline(0.0075,c='k',ls=':'); ax[0].set_xscale('log'); ax[0].set_xlabel(r'$c=\tau/S$ (постоянная времени звена / длина паттерна)'); ax[0].set_ylabel('sep margin'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[0].set_title('Пассивный кабель, Classic, dt=0.05 мс: коллапс по c=τ/S')
ax[1].axhline(0.1,c='r',ls='--'); ax[1].set_xlabel('FWHM самого длинного ядра / S'); ax[1].set_ylabel('margin, сдвиг S/4'); ax[1].grid(alpha=.3); ax[1].legend()
plt.tight_layout(); plt.savefig('../fig2_margin_vs_c_collapse.png',dpi=130)
# dispersion law: sigma of the tap with delay d=S depends only on tau (sigma^2 = d*tau); dt only bounds tau from below
fig,ax=plt.subplots(figsize=(6.6,4.5)); c=np.logspace(-3.5,-0.5,300)
ax.plot(c,np.sqrt(c),'b-',lw=2,label=r'$\sigma_S/S=\sqrt{\tau/S}$ (отвод с задержкой $d=S$)')
for eta,lab,col in ((0.02,'dt=0.5 мс, S25: τ>dt','C3'),(0.002,'dt=0.05 мс, S25','C2'),(0.0005,'dt=0.05 мс, S100','C1')):
    ax.axvline(eta,c=col,ls=':',label=lab+f' (τ/S > {eta})')
ax.axhline(0.072,c='r',ls='--',label='нужно для сдвига S/4'); ax.axhline(0.038,c='m',ls='--',label='нужно для 8 паттернов')
ax.axvline(0.0075,c='k',ls='-.',label=r'численный порог $\tau\leq0.0075S$')
ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel(r'$c=\tau/S$ (постоянная времени звена)'); ax.set_ylabel(r'$\sigma/S$')
ax.legend(fontsize=6.5); ax.grid(alpha=.3,which='both'); ax.set_title('Ширина ядра задаётся τ звена; L=d/(τ−dt) — следствие')
plt.tight_layout(); plt.savefig('../fig4_dispersion_bound.png',dpi=130)
# high-pass
H=json.load(open('../data/run_hp.json')); fig,ax=plt.subplots(figsize=(6,4.3))
for th in (0.02,0.05,0.1,0.2):
    r=[x for x in H if x['tau_h_over_S']==th]; ax.plot([x['beta'] for x in r],[x['s4'] for x in r],'-o',ms=3,label=f'τh/S={th}: S/4')
r=[x for x in H if x['tau_h_over_S']==0.1]; ax.plot([x['beta'] for x in r],[x['m8'] for x in r],'k--',label='τh/S=0.1: 8 паттернов')
ax.axhline(0.1,c='r',ls='--'); ax.set_xlabel(r'$\beta$ (доля вычитаемой медленной компоненты)'); ax.set_ylabel('sep margin'); ax.grid(alpha=.3); ax.legend(fontsize=8)
ax.set_title('τ/S=0.012 (L≤100) + подпороговая гиперполяризация сомы'); plt.tight_layout(); plt.savefig('../fig5_soma_highpass.png',dpi=130)
# tails
tb=np.load('../data/tail_base.npy'); a=np.load('../data/trace_fast_spike.npy'); b=np.load('../data/trace_fast_nospike.npy')
fig,ax=plt.subplots(1,2,figsize=(12,4))
ax[0].plot(tb[:,0],tb[:,1]); ax[0].axhline(0,c='k',lw=.5); ax[0].set_xlabel('t, с'); ax[0].set_title('C1e9, dt=0.5 мс, L=[7,6,4,1]+nextseg: хвост торможения'); ax[0].grid(alpha=.3)
S=0.025; ax[1].plot(b[:,0]/S,b[:,1],label='без порога'); ax[1].plot(a[:,0]/S,a[:,1],label='с порогом 0.97·P0 (спайк)'); ax[1].set_xlabel('t/S'); ax[1].set_title('Быстрый набор F1 (S25, Branch): потенциал сомы'); ax[1].legend(); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig('../fig6_tails_iti.png',dpi=130)
