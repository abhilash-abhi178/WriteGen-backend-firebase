# convert LaTeX to SVG (using latex -> dvisvgm or latex2svg library)
import os
import tempfile
from typing import Tuple
import subprocess

class LatexService:
    def __init__(self, workdir: str = "/tmp"):
        self.workdir = workdir

    async def latex_to_svg(self, latex: str) -> str:
        """
        Minimal pipeline:
        - Create .tex, run latex -> dvi -> dvisvgm to get SVG
        Assumes latex + dvisvgm installed on host.
        """
        with tempfile.TemporaryDirectory(dir=self.workdir) as td:
            tex_path = os.path.join(td, "eq.tex")
            svg_path = os.path.join(td, "eq.svg")
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write("\\documentclass{standalone}\n\\usepackage{amsmath}\n\\begin{document}\n")
                f.write(latex)
                f.write("\n\\end{document}")
            # run latex (pdflatex would create pdf; we want dvi path)
            subprocess.run(["latex", "-interaction=nonstopmode", tex_path], cwd=td, check=True)
            # dvisvgm
            # find .dvi file
            dvi = next((os.path.join(td, f) for f in os.listdir(td) if f.endswith(".dvi")), None)
            if dvi is None:
                raise RuntimeError("DVI not generated")
            subprocess.run(["dvisvgm", dvi, "-n", "-o", svg_path], cwd=td, check=True)
            # copy svg to outputs
            out_svg = os.path.join(self.workdir, f"latex_{int(os.times().system*1000)}.svg")
            os.replace(svg_path, out_svg)
            return out_svg
