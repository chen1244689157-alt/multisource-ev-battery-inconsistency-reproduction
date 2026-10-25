from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import export_settings
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "fig_03"
OUT.mkdir(parents=True, exist_ok=True)
d = pd.read_csv(ROOT / "data" / "fig_03" / "vehicle_scores.csv")
d = d.rename(columns={"vehicle_alias":"vehicle_id", "risk_score_mV":"risk_score", "risk_grade":"risk_level"})
d["risk_level"] = d.risk_level.replace({"low":"normal"})
cohort_source = d.cohort.copy()
d["domain"] = cohort_source.map({"A_train":"model_A", "A_test":"model_A", "B_train":"model_B", "B_test":"model_B", "C_independent":"domain_C"})
d["cohort"] = cohort_source.map({"A_train":"train", "A_test":"test", "B_train":"train", "B_test":"test", "C_independent":"independent"})
assert len(d)==98 and d.vehicle_id.nunique()==98

groups = [
    ("model_A", "train", "A train", "A train"),
    ("model_B", "train", "B train", "B train"),
    ("model_A", "test", "A test", "A test"),
    ("model_B", "test", "B test", "B test"),
    ("domain_C", "independent", "C", "C"),
]
colors = {"normal":"#5797CE", "medium":"#329D8D", "high":"#DF756A"}

mpl.rcParams.update({
    "font.family":"sans-serif", "font.sans-serif":["Arial","DejaVu Sans"],
    "font.size":7, "axes.titlesize":8, "axes.labelsize":7,
    "xtick.labelsize":6.5, "ytick.labelsize":6.5, "axes.linewidth":.65,
    "pdf.fonttype":42, "svg.fonttype":"none", "legend.fontsize":6.5,
})

fig, axes = plt.subplots(2, 3, figsize=(7.48, 3.89))
fig.subplots_adjust(left=.075, right=.985, bottom=.105, top=.84, wspace=.48, hspace=.62)
handles = [Patch(facecolor=colors[k], label=k.capitalize()) for k in colors]
handles += [Line2D([0],[0],color="#59616B",ls="--",lw=.8,label="75th percentile"),
            Line2D([0],[0],color="#59616B",ls=":",lw=1,label="90th percentile")]
fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5,.995), ncol=5,
           frameon=False, columnspacing=1.2, handlelength=1.7)

qA = tuple(d[(d.domain=="model_A") & (d.cohort=="train")].risk_score.quantile([.75,.90]))
qB = tuple(d[(d.domain=="model_B") & (d.cohort=="train")].risk_score.quantile([.75,.90]))
qC = tuple(d[(d.domain=="domain_C") & (d.cohort=="independent")].risk_score.quantile([.75,.90]))
frozen = {("model_A","train"):qA, ("model_A","test"):qA,
          ("model_B","train"):qB, ("model_B","test"):qB,
          ("domain_C","independent"):qC}

counts=[]; thresholds=[]; rows=[]
for idx, (domain, cohort, panel_title, bar_label) in enumerate(groups):
    ax=axes.flat[idx]
    g=d[(d.domain==domain)&(d.cohort==cohort)].sort_values(["risk_score","vehicle_id"]).copy()
    g["rank"]=np.arange(1,len(g)+1)
    q75,q90=frozen[(domain,cohort)]
    expected=np.where(g.risk_score+1e-12>=q90,"high",np.where(g.risk_score+1e-12>=q75,"medium","normal"))
    assert np.array_equal(expected,g.risk_level.to_numpy())
    for risk,color in colors.items():
        z=g[g.risk_level==risk]
        ax.scatter(z["rank"],z.risk_score,s=19,color=color,edgecolor="white",linewidth=.35,zorder=3)
    ax.axhline(q75,color="#59616B",ls="--",lw=.8)
    ax.axhline(q90,color="#59616B",ls=":",lw=1)
    ax.set_xlim(.2,len(g)+.8); ax.set_ylim(0,max(g.risk_score.max()*1.17,.1))
    ax.set_title(f"{panel_title} (n = {len(g)})",pad=6)
    ax.set_xlabel("Vehicle rank"); ax.set_ylabel("Voltage trend score (mV)")
    ax.text(-.25,1.10,"abcde"[idx],transform=ax.transAxes,fontsize=10,fontweight="bold")
    counts.append([int((g.risk_level==k).sum()) for k in colors])
    thresholds.append({"group":bar_label,"q75_mV":q75,"q90_mV":q90})
    rows.append(g)

ax=axes.flat[5]; y=np.arange(5); left=np.zeros(5)
for j,risk in enumerate(colors):
    vals=np.asarray(counts)[:,j]
    ax.barh(y,vals,left=left,height=.64,color=colors[risk],edgecolor="white",linewidth=.5)
    for yy,v,lft in zip(y,vals,left):
        if v: ax.text(lft+v/2,yy,str(v),ha="center",va="center",fontsize=6.5,color="#142838")
    left+=vals
ax.set_yticks(y,[g[3] for g in groups]); ax.invert_yaxis(); ax.set_xlim(0,33)
ax.set_xlabel("Number of vehicles"); ax.set_title("(n = 98)",pad=6)
ax.text(-.25,1.10,"f",transform=ax.transAxes,fontsize=10,fontweight="bold")

for ax in axes.flat:
    for s in ax.spines.values(): s.set_visible(True); s.set_linewidth(.65); s.set_color("#626870")
    ax.tick_params(direction="out",length=2.5,width=.6,top=False,right=False,labeltop=False,labelright=False)
    ax.set_box_aspect(.60)

stem=OUT/"fig_03"
fig.savefig(str(stem)+".png",dpi=600,facecolor="white")
fig.savefig(str(stem)+".pdf",facecolor="white")
fig.savefig(str(stem)+".svg",facecolor="white")
fig.savefig(str(stem)+".tiff",dpi=600,facecolor="white",pil_kwargs={"compression":"tiff_lzw"})
plt.close(fig)
