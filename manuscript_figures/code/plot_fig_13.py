from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import export_settings
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap,Normalize

from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'fig_13'
OUT=ROOT/'outputs'/'fig_13'
OUT.mkdir(parents=True,exist_ok=True)
z=pd.read_csv(DATA/'score_distribution.csv')
m=pd.read_csv(DATA/'method_metrics.csv')
lo=pd.read_csv(DATA/'non_alarm_sessions.csv')
hi=pd.read_csv(DATA/'high_score_sessions.csv')
low=SimpleNamespace(car=100);high=SimpleNamespace(car=107)
assert len(z)==347 and len(lo)==431 and len(hi)==42
mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
 'font.size':7,'axes.labelsize':7,'axes.titlesize':8,'xtick.labelsize':7,'ytick.labelsize':7,
 'axes.spines.top':True,'axes.spines.right':True,'xtick.top':False,'ytick.right':False,
 'axes.linewidth':.65,'svg.fonttype':'none','pdf.fonttype':42,'legend.frameon':False})
fig,axes=plt.subplots(3,2,figsize=(7.48,6.15))
fig.subplots_adjust(left=.09,right=.90,bottom=.12,top=.86,hspace=.68,wspace=.36)
ax=axes[0,0]
brandcolors=['#397CB3','#57B89C','#79609C']
for k,(brand,g) in enumerate(z.groupby('brand',sort=True)):
 values=np.sort(g.threshold_ratio.to_numpy()); x=np.arange(1,len(g)+1)/len(g)*100
 ax.plot(x,values,color=brandcolors[k],lw=.8,label=f'Brand {k+1} (n = {len(g)})')
ax.axhline(1,color='#D9675D',lw=.8,ls='--',label='Calibrated threshold'); ax.set_xlabel('Within-brand score percentile (%)'); ax.set_ylabel('Score / calibrated threshold')
ax.set_title('Vehicle-held-out scores (5-fold CV, n = 347)',pad=8); ax.legend(loc='upper left',fontsize=6.5)
ax=axes[0,1]; metriccols=['accuracy','specificity','false_positive_rate']; x=np.arange(3)
methods=[('mlp_alarm','Conditional MLP','#57B89C')]
for k,(key,name,color) in enumerate(methods):
 row=m[m.method.eq(key)].iloc[0]; assert int(row.n)==347
 bars=ax.bar(x,[row[c]*100 for c in metriccols],.62,color=color,edgecolor='#555555',lw=.35,label=name)
 ax.bar_label(bars,fmt='%.0f',padding=1,fontsize=6)
ax.set_xticks(x,['Accuracy','Specificity','False-positive\nrate']); ax.set_xlim(-.65,2.65); ax.set_ylim(0,112); ax.set_yticks([0,50,100]); ax.set_ylabel('Metric (%)')
ax.set_title('Conditional-response MLP performance',pad=8)
case_data=pd.concat([lo,hi]); vmin=float(case_data.current_median_A.min()); vmax=float(case_data.current_median_A.max())
cmap=LinearSegmentedColormap.from_list('current',['#D4EDD3','#68BFA6','#568DBB','#8C80B1']); norm=Normalize(vmin=vmin,vmax=vmax)
spread_max=float(case_data.cell_spread_p95_mV.max()); spread_min=float(case_data.cell_spread_p95_mV.min())
for ax,g,row,descriptor in [(axes[1,0],lo,low,'Non-alarm case'),(axes[1,1],hi,high,'High-score case')]:
 sc=ax.scatter(g.soc_median_pct,g.cell_spread_p95_mV,c=g.current_median_A,cmap=cmap,norm=norm,
  s=8,alpha=.85,edgecolors='none',rasterized=True)
 ax.set_xlim(-2,102); ax.set_ylim(min(0,spread_min),spread_max*1.1); ax.set_xlabel('Session SOC median (%)'); ax.set_ylabel('Session voltage spread P95 (mV)')
 ax.set_title(f"Brand 1, vehicle {int(row.car)}: {descriptor} (n = {len(g)})",fontsize=7,pad=8)
cax=fig.add_axes([.91,.39,.012,.23]); cb=fig.colorbar(sc,cax=cax); cb.ax.set_title('Charging\ncurrent (A)',fontsize=7,pad=7); cb.ax.tick_params(labelsize=6.5,pad=2)
for ax,col,ylabel in [(axes[2,0],'min_cell_p05_V','Session minimum-cell voltage P5 (V)'),(axes[2,1],'temp_spread_p95_C','Session temperature spread P95 (°C)')]:
 for g,row,color,marker,name in [(lo,low,'#568DBB','o','Non-alarm'),(hi,high,'#D9675D','D','High-score')]:
  ax.scatter(g.soc_median_pct,g[col],s=8 if marker=='o' else 12,c=color,marker=marker,alpha=.75,edgecolors='none',rasterized=True)
 ax.set_xlim(-2,102); ax.set_xlabel('Session SOC median (%)'); ax.set_ylabel(ylabel)
ax=axes[2,0]; ax.set_title('Minimum-cell voltage response',pad=8)
axes[2,1].set_title('Pack temperature dispersion',pad=8)
for ax,label in zip(axes.flat,'abcdef'): ax.text(.01,1.14,label,transform=ax.transAxes,fontweight='bold',fontsize=10)
handles=[Line2D([],[],marker='o',color='#568DBB',ls='none',ms=3,label=f'Vehicle {int(low.car)}: non-alarm'),
 Line2D([],[],marker='D',color='#D9675D',ls='none',ms=3,label=f'Vehicle {int(high.car)}: high score')]
fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.29,.98),ncol=2,fontsize=7,columnspacing=2)
stem=OUT/'fig_13'
fig.savefig(str(stem)+'.pdf',facecolor='white'); fig.savefig(str(stem)+'.svg',facecolor='white')
fig.savefig(str(stem)+'.png',dpi=600,facecolor='white'); fig.savefig(str(stem)+'.tiff',dpi=600,facecolor='white',pil_kwargs={'compression':'tiff_lzw'})
plt.close(fig)
