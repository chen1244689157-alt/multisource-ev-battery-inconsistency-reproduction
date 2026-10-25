"""Figure 4: traceable voltage evidence in three same-cohort examples."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import export_settings
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'fig_04'
OUT=ROOT/'outputs'/'fig_04'
OUT.mkdir(parents=True,exist_ok=True)
cases=[('A-TR-23','Normal'),('A-TR-02','Medium'),('A-TR-01','High')]
palette={'blue':'#397CB3','band':'#A9CBE2','teal':'#268F81','purple':'#79609C','coral':'#D9675D','gray':'#58636D'}
mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':7,'axes.titlesize':8,'axes.labelsize':7,'xtick.labelsize':6.5,'ytick.labelsize':6.5,'axes.linewidth':.65,'pdf.fonttype':42,'svg.fonttype':'none','legend.fontsize':6.5})
fig,axs=plt.subplots(3,3,figsize=(7.20,5.9));fig.subplots_adjust(left=.075,right=.915,bottom=.11,top=.915,wspace=.70,hspace=.70)
fig.legend(handles=[
    Line2D([0],[0],color=palette['coral'],lw=.9,label='Voltage score-leading cell'),
    Patch(facecolor=palette['band'],label='Other-cell P10–P90'),
    Line2D([0],[0],color=palette['purple'],lw=.9,label='Late 20%'),
    Line2D([0],[0],color=palette['teal'],lw=.9,label='Early 20%')],
    loc='upper center',bbox_to_anchor=(.5,.995),ncol=4,frameon=False)
summaries=[]
for col,(vid,display) in enumerate(cases):
    g=pd.read_csv(DATA/f'{vid}_relative_voltage.csv')
    stages=pd.read_csv(DATA/f'{vid}_early_late_cells.csv')
    days=g.elapsed_days.to_numpy(float); n=len(g); e=max(1,int(.2*n));tail=max(e+1,int(.8*n))
    top=int(stages.loc[stages.tail_score.idxmax(),'cell_index'])
    early=stages.early_median_mV.to_numpy(float);late=stages.late_median_mV.to_numpy(float)
    change=stages.change_mV.to_numpy(float)
    gap=np.r_[False,np.diff(days)*86400>7200.00001]
    line=g.candidate_relative_mV.to_numpy(float).copy()
    loline=g.other_P10_mV.to_numpy(float).copy();hiline=g.other_P90_mV.to_numpy(float).copy()
    line[gap]=np.nan;loline[gap]=np.nan;hiline[gap]=np.nan
    ax=axs[0,col]
    ax.axvspan(days[0],days[e-1],color=palette['teal'],alpha=.09,zorder=0)
    ax.axvspan(days[tail],days[-1],color=palette['purple'],alpha=.09,zorder=0)
    ax.fill_between(days,loline,hiline,color=palette['band'],alpha=1.0,
                    linewidth=0,zorder=1)
    ax.plot(days,loline,color=palette['blue'],lw=.35,zorder=2)
    ax.plot(days,hiline,color=palette['blue'],lw=.35,zorder=2)
    ax.axhline(0,color=palette['gray'],lw=.55);ax.axhline(-3,color=palette['gray'],lw=.55,ls='--')
    ax.plot(days,line,color=palette['coral'],lw=.62,zorder=3)
    riskcolor={'Normal':palette['blue'],'Medium':palette['teal'],'High':palette['coral']}[display]
    ax.set_title(f'{display}: {vid} / Cell{top}',color='black',pad=6)
    ax.set_ylim(-50,35);ax.set_ylabel('Relative voltage (mV)');ax.set_xlabel('Elapsed time (days)')
    ax=axs[1,col];indices=np.arange(1,96)
    ax.plot(indices,early,color=palette['teal'],lw=.75,marker='o',ms=1.6)
    ax.plot(indices,late,color=palette['purple'],lw=.75,marker='o',ms=1.6)
    ax.axvline(top,color=palette['gray'],lw=.5,ls=':');ax.axhline(0,color=palette['gray'],lw=.5)
    ax.scatter([top],[late[top-1]],s=24,facecolor=palette['coral'],edgecolor='white',linewidth=.4,zorder=4)
    ax.set_xlim(0,96);ax.set_ylim(-18,6);ax.set_ylabel('Stage median (mV)');ax.set_xlabel('Cell index');ax.set_title(f'Early–late profiles: change {change[top-1]:.0f} mV',pad=6)
    ax=axs[2,col];right=ax.twinx()
    soc=g.SOC_percent.to_numpy(float,copy=True);current=g.current_A.to_numpy(float,copy=True);soc[gap]=np.nan;current[gap]=np.nan
    ax.plot(days,soc,color=palette['blue'],lw=.65);right.plot(days,current,color=palette['teal'],lw=.5,alpha=.85)
    ax.set_ylim(0,105);ax.set_ylabel('SOC (%)',color='black');right.set_ylabel('Current (A)',color='black')
    ax.tick_params(axis='y',labelcolor='black')
    right.tick_params(axis='y',labelsize=6.5,direction='out',length=2.5,width=.6,colors='black');right.tick_params(axis='x',top=False,labeltop=False)
    for sp in right.spines.values():sp.set_visible(False)
    ax.set_xlabel('Elapsed time (days)');ax.set_title('Operating conditions',pad=6)
    for row in range(3):
        a=axs[row,col];a.text(-.28,1.10,'abcdefghi'[row*3+col],transform=a.transAxes,fontsize=10,fontweight='bold')
        for spine in a.spines.values():spine.set_visible(True);spine.set_color('#626870');spine.set_linewidth(.65)
        a.tick_params(direction='out',length=2.5,width=.6,top=False,right=False,labeltop=False,labelright=False)
        # Set adjustable aspect for twin axes through the shared physical subplot grid.
b=OUT/'fig_04'
fig.savefig(str(b)+'.png',dpi=600);fig.savefig(str(b)+'.pdf');fig.savefig(str(b)+'.svg');fig.savefig(str(b)+'.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'})
plt.close(fig)
