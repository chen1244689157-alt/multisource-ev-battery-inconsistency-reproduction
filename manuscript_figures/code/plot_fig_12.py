"""Calendar-progress prefix replay: fixed retrospective cohort thresholds.
All released observations contribute to each prefix score. Display bins span
0.5% of the vehicle observation window; bins without observations stay missing.
"""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import export_settings
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'/'fig_12'
OUT.mkdir(parents=True,exist_ok=True)
CASES=['A-TR-23','A-TR-02','A-TR-01']
GROUPS=[('A','train','A train'),('B','train','B train'),('A','test','A test'),('B','test','B test'),('C','independent','C')]
COLORS=['#DDE2E6','#5797CE','#329D8D','#DF756A']
warnings.filterwarnings('ignore',message='All-NaN slice encountered')

def draw(d):
    mpl.rcParams.update({'font.family':'Arial','font.size':7,'axes.titlesize':8,'axes.labelsize':7,
                         'xtick.labelsize':6.5,'ytick.labelsize':6.5,'pdf.fonttype':42,
                         'pdf.compression':0,'svg.fonttype':'none','path.simplify':False})
    fig=plt.figure(figsize=(7.2,5.62))
    gs=fig.add_gridspec(3,2,left=.085,right=.96,bottom=.08,top=.83,width_ratios=[1,1.14],wspace=.36,hspace=.52)
    names=['A-TR-23 | Final: low','A-TR-02 | Final: medium','A-TR-01 | Final: high']
    for i,(vid,name) in enumerate(zip(CASES,names)):
        ax=fig.add_subplot(gs[i,0]); g=d[d.vehicle_id==vid].sort_values('bin')
        x=g.elapsed_days.to_numpy(); y=g.score_mV.to_numpy().copy()
        y[g.display_state.to_numpy()<0]=np.nan
        ax.plot(x,y,color='#365F7E',lw=.85,zorder=2)
        for state,color in enumerate(COLORS[1:]):
            keep=g.display_state.eq(state)
            # Use Line2D markers instead of PathCollection scatter objects.
            # This avoids partial marker loss in some Adobe PDF renderers.
            ax.plot(x[keep],y[keep],linestyle='None',marker='o',markersize=2.25,
                    markerfacecolor=color,markeredgecolor=color,markeredgewidth=0,
                    zorder=3)
        ax.axhline(g.q75.iloc[0],color='#606D78',ls='--',lw=.7)
        ax.axhline(g.q90.iloc[0],color='#606D78',ls=':',lw=.9)
        ax.set_xlim(0,x[-1]); ax.set_ylim(bottom=0)
        ax.set_ylabel('Voltage score (mV)'); ax.set_xlabel('Elapsed time (days)')
        ax.set_title(name,pad=5)
        ax.text(-.18,1.06,'abc'[i],transform=ax.transAxes,fontsize=10,fontweight='bold')
    ax=fig.add_subplot(gs[:,1])
    ids=d.vehicle_id.drop_duplicates().tolist()
    mat=d.pivot(index='vehicle_id',columns='bin',values='display_state').reindex(ids).to_numpy()+1
    cmap=ListedColormap(COLORS)
    # Export the heatmap as opaque vector cells rather than an embedded raster
    # image so that Adobe Acrobat does not drop image tiles on redraw/zoom.
    x_edges=np.linspace(0,100,mat.shape[1]+1)
    y_edges=np.arange(mat.shape[0]+1)
    ax.pcolormesh(x_edges,y_edges,mat,cmap=cmap,
                  norm=BoundaryNorm(np.arange(-.5,4.5),4),shading='flat',
                  edgecolors='none',linewidth=0,antialiased=False,rasterized=False)
    ax.set_xlim(0,100);ax.set_ylim(98,0)
    start=0; centers=[]; labels=[]; order=[]
    for _,_,group in GROUPS:
        g=d[d.group==group]; n=g.vehicle_id.nunique()
        centers.append(start+n/2);labels.append(f'{group}\n(n = {n})')
        if start: ax.axhline(start,color='white',lw=1)
        start+=n
    ax.set_yticks(centers,labels);ax.set_xlabel('Elapsed observation period (%)')
    ax.set_title('Risk-state evolution: all 98 vehicles',pad=5)
    ax.text(-.16,1.02,'d',transform=ax.transAxes,fontsize=10,fontweight='bold')
    for vid,letter in zip(CASES,'abc'):
        y=ids.index(vid)+.5
        ax.text(101.2,y,letter,ha='left',va='center',fontsize=6.5,fontweight='bold')
    for axis in fig.axes:
        axis.tick_params(top=False,right=False,length=2.5,width=.6)
        for sp in axis.spines.values():sp.set_visible(True);sp.set_color('#626870');sp.set_linewidth(.65)
    keys=[Patch(facecolor=c,label=n) for c,n in zip(COLORS,['Unavailable / no observation','Low','Medium','High'])]
    fig.legend(handles=keys,loc='upper center',bbox_to_anchor=(.52,.99),ncol=4,frameon=False,fontsize=6.5,handlelength=1.1,columnspacing=1)
    keys=[Line2D([],[],color='#606D78',ls='--',label='75th-percentile threshold'),Line2D([],[],color='#606D78',ls=':',label='90th-percentile threshold')]
    fig.legend(handles=keys,loc='upper center',bbox_to_anchor=(.50,.94),ncol=2,frameon=False,fontsize=6.5)
    stem=OUT/'fig_12'
    fig.savefig(str(stem)+'.png',dpi=600)
    fig.savefig(str(stem)+'.pdf')
    fig.savefig(str(stem)+'.svg')
    fig.savefig(str(stem)+'.tiff',dpi=600)
    plt.close(fig)
    pd.DataFrame({'heatmap_row':np.arange(1,99),'vehicle_id':ids}).to_csv(OUT/'heatmap_row_ids.csv',index=False)
    last=d.sort_values('bin').groupby('vehicle_id').tail(1)
    stat=[]
    for vid,g in d.groupby('vehicle_id',sort=False):
        valid=g[g.display_state>=0]
        stat.append(dict(vehicle_id=vid,final_risk=g.final_risk.iloc[0],displayable_bins=len(valid),
                         positive_bins=int((valid.display_state>=1).sum()),
                         high_bins=int((valid.display_state==2).sum())))
    pd.DataFrame(stat).to_csv(OUT/'state_summary.csv',index=False)

if __name__=='__main__':
    d=pd.read_csv(ROOT/'data'/'fig_12'/'prefix_replay.csv.gz')
    d=d.rename(columns={'vehicle_alias':'vehicle_id','cohort':'group','q75_mV':'q75','q90_mV':'q90'})
    d['group']=d['group'].replace({'A_train':'A train','B_train':'B train','A_test':'A test','B_test':'B test','C_independent':'C'})
    assert d.vehicle_id.nunique()==98
    draw(d)
