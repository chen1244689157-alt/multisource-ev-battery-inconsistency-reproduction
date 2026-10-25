from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import export_settings
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'fig_05'
OUT=ROOT/'outputs'/'fig_05'
OUT.mkdir(parents=True,exist_ok=True)
CASES=[('A-TR-23',2,'Normal: A-TR-23'),('A-TR-02',26,'Medium: A-TR-02'),('A-TR-01',25,'High: A-TR-01')]
mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans','Arial','DejaVu Sans'],
 'font.size':7,'axes.labelsize':7,'axes.titlesize':8,'xtick.labelsize':7,'ytick.labelsize':7,
 'axes.spines.top':True,'axes.spines.right':True,'xtick.top':False,'ytick.right':False,
 'axes.linewidth':.65,'svg.fonttype':'none','pdf.fonttype':42,'legend.frameon':False})
fig=plt.figure(figsize=(7.48,2.7))
gs=fig.add_gridspec(1,3,left=.08,right=.985,bottom=.28,top=.67,wspace=.48)
summaries=[]
for j,(vehicle,cell,title) in enumerate(CASES):
 late=pd.read_csv(DATA/f'{vehicle}_matched_late_observations.csv')
 supported=late[late.reference_supported].copy()
 curve=pd.read_csv(DATA/f'{vehicle}_soc_condition_curve.csv')
 ax=fig.add_subplot(gs[0,j]); ax.set_title(f'{title} | Cell{cell}',pad=8)
 if len(curve):
  x=curve.SOC.to_numpy(); ref=curve.reference.to_numpy(); actual=curve.late.to_numpy()
  ax.fill_between(x,curve.ref_low.to_numpy(),curve.ref_high.to_numpy(),color='#397CB3',alpha=.30,lw=0)
  ax.plot(x,ref,'o-',color='#397CB3',lw=.8,ms=2.5)
  ax.plot(x,actual,'D-',color='#D9675D',lw=.8,ms=2.5)
 ax.axhline(0,color='#555555',lw=.5,ls='--')
 ax.set_xlim(0,100); ax.set_xticks([0,50,100]); ax.set_xlabel('SOC (%)')
 if j==0: ax.set_ylabel('Relative voltage (mV)')
 ax.text(-.24,1.12,chr(97+j),transform=ax.transAxes,fontweight='bold',fontsize=10)
 coverage=len(supported)/len(late)
 ax.set_ylim(-14,2)
 ax.text(.5,-.43,f'Reference coverage: {len(supported)}/{len(late)} ({coverage:.1%})',transform=ax.transAxes,ha='center',fontsize=7,color='#555555')
fig.legend(handles=[Line2D([],[],color='#397CB3',marker='o',lw=.8,ms=3,label='Matched early reference'),
 Patch(facecolor='#397CB3',alpha=.30,label='Reference P25–P75'),
 Line2D([],[],color='#D9675D',marker='D',lw=.8,ms=3,label='Late observation')],
 loc='upper left',bbox_to_anchor=(.075,.99),ncol=2,fontsize=7,columnspacing=1.7)
fig.text(.08,.045,'Matched conditions: SOC ±5 pp; current ±20 A; temperature ±5 °C; same charging state.',fontsize=7,color='#555555')
stem=OUT/'fig_05'
fig.savefig(str(stem)+'.pdf',facecolor='white'); fig.savefig(str(stem)+'.svg',facecolor='white')
fig.savefig(str(stem)+'.png',dpi=600,facecolor='white')
fig.savefig(str(stem)+'.tiff',dpi=600,facecolor='white',pil_kwargs={'compression':'tiff_lzw'})
plt.close(fig)
