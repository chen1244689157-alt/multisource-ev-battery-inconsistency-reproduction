"""Export the final schematic artwork; this is not numerical plot regeneration."""
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'/'fig_01'
OUT.mkdir(parents=True,exist_ok=True)
im=Image.open(ROOT/'data'/'fig_01'/'schematic.png').convert('RGB')
im.save(OUT/'fig_01.png',dpi=(600,600))
im.save(OUT/'fig_01.tiff',dpi=(600,600),compression='tiff_lzw')
im.save(OUT/'fig_01.pdf',resolution=600,title='Figure 1',author='',creator='',creationDate='',modDate='')
