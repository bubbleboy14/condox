import re
from condox.util import getstart, colormap
from .rules import *
from ..util import nextlast, trans, Converter

#
# tables
#

TSEP = '</tr>'
TBL = "\\begin{tabular}{%s}%s\\end{tabular}"
CELL_RE = re.compile(r"<(td|th)([^>]*)>(.*?)</\1>", re.I | re.S)
WIDTH_RE = re.compile(r"width\s*:\s*([^;\"']+)", re.I)
BG_RE = re.compile(r"background-color\s*:\s*([^;\"']+)", re.I)
COLSPAN_RE = re.compile(r"colspan=[\"']?(\d+)", re.I)
TBODY_RE = re.compile(r"</?(tbody|thead|tfoot)[^>]*>", re.I)

def attr_width(attrs):
	match = WIDTH_RE.search(attrs)
	if not match:
		return None
	val = match.group(1).strip()
	if val.endswith("%"):
		try:
			return float(val[:-1]) / 100.0
		except ValueError:
			return None
	try:
		return float(val.rstrip("px"))
	except ValueError:
		return None

def attr_background(attrs):
	match = BG_RE.search(attrs)
	return match.group(1).strip() if match else None

def colspec(widths):
	if not widths:
		return "| p{0.98\\linewidth} |"
	if any(w > 1 for w in widths):
		total = sum(widths)
		widths = [w / total for w in widths]
	else:
		total = sum(widths)
		if total and total > 1:
			widths = [w / total for w in widths]
	widths = [max(0.04, w * 0.92) for w in widths]
	return "| %s |"%(" | ".join(["p{%.3f\\linewidth}"%(w,) for w in widths]),)

def row_cells(chunk, table_bg=None):
	cells = []
	widths = []
	row_attrs = chunk.split(">", 1)[0]
	row_bg = attr_background(row_attrs)
	for match in CELL_RE.finditer(chunk):
		tag, attrs, body = match.groups()
		cell = trans("<%s%s>%s</%s>"%(tag, attrs, body, tag),
			tag.lower(), tflags[tag.lower()], cstyles=tcstyles, listed=True)[0]
		cell_bg = attr_background(attrs)
		inherited_bg = cell_bg or row_bg or table_bg
		if inherited_bg and not cell_bg:
			cell = "\\cellcolor{%s}%s"%(colormap(inherited_bg), cell)
		span_match = COLSPAN_RE.search(attrs)
		colspan = int(span_match.group(1)) if span_match else 1
		width = attr_width(attrs)
		cells.append((cell, colspan))
		for _ in range(colspan):
			widths.append(width / colspan if width else None)
	if not cells:
		return [], []
	return cells, widths

def row(chunk, table_bg=None):
	cells, widths = row_cells(chunk, table_bg)
	return [cell for cell, colspan in cells], widths

def table(seg, starter=""):
	preamble = ""
	table_bg = attr_background(starter)
	if not seg.startswith("<tr"):
		preamble, seg = seg.split("<tr", 1)
		preamble = TBODY_RE.sub("", preamble)
		seg = "<tr%s"%(seg,)
	parsed = [row(chunk, table_bg) for chunk in seg.split(TSEP)]
	rowz = [r for r, widths in parsed if r]
	widthz = [widths for r, widths in parsed if r]
	if not rowz:
		return preamble
	numcols = max([len(r) for r in rowz])
	widths = []
	for c in range(numcols):
		vals = [w[c] for w in widthz if c < len(w) and w[c]]
		widths.append(vals[0] if vals else 1.0 / numcols)
	for r in rowz:
		if len(r) == 1 and numcols > 1:
			r[0] = "\\multicolumn{%s}{|p{0.920\\linewidth}|}{%s}"%(numcols, r[0])
		while len(r) < numcols and not r[0].startswith("\\multicolumn"):
			r.append(" ")
	return preamble + "\\begingroup\n\\small\n\\setlength{\\tabcolsep}{3pt}\n\\renewcommand{\\arraystretch}{1.2}\n" + TBL%(colspec(widths),
		"\n\\hline\n%s\\\\\n\\hline\n"%("\\\\\n\\hline\n".join([" & ".join(r) for r in rowz]),)) + "\n\\endgroup"

TABLE_FLAGS = {
	"startend": '>',
	"end": '</table>',
	"nostyle": True,
	"handler": table
}

def rowsets(rows):
	sets = []
	curnum = None
	while len(rows):
		item = rows.pop(0)
		if curnum != len(item):
			curnum = len(item)
			if curnum == 1:
				curset = []
			else:
				curset = [["   "] * curnum]
			sets.append(curset)
		curset.append(item)
	if len(sets) == 1:
		sets[0].pop(0)
	return sets

def bartable(rowz):
	if not rowz:
		return ""
	numcols = len(rowz[0])
	if numcols == 1 and len(rowz) == 1:
		return "\\begin{center}\n%s\n\\end{center}"%(rowz[0][0],)
	rowz = [rowz[0]] + [["-" * 30] * numcols] + rowz[1:]
	return "\n%s"%("\n".join(["| %s |"%(" | ".join(r),) for r in rowz]),)
