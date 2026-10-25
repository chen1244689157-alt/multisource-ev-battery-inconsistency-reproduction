"""Consistent exports with no author or generation-time metadata."""
from pathlib import Path
from matplotlib.figure import Figure
_ORIGINAL=Figure.savefig
def _save(self,fname,*args,**kwargs):
    ext=Path(str(fname)).suffix.lower()
    if ext=='.svg':kwargs['metadata']={'Date':None,'Creator':'Figure reproduction'}
    elif ext=='.pdf':kwargs['metadata']={'CreationDate':None,'ModDate':None,'Author':'','Creator':'Figure reproduction'}
    return _ORIGINAL(self,fname,*args,**kwargs)
Figure.savefig=_save
