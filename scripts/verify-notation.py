"""Check the course notation contract without rewriting executable Python cells.

This guards the symbol families at the ROM/EIM/GEIM/PBDW interfaces. It is
not a claim to establish that every mathematical symbol has a semantic definition.
"""
from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parents[1]
failures = []
files = list((ROOT/'materials/modules/ROOT/pages').rglob('*.adoc'))
files += list((ROOT/'docs/modules/ROOT/pages/labs').glob('*.adoc'))
for path in files:
    text = path.read_text()
    for index, block in enumerate(re.finditer(
            r'\[source[^\n]*,python[^\n]*\]\n----\n(.*?)\n----', text, re.S)):
        try:
            ast.parse(block[1])
        except SyntaxError as error:
            failures.append(f'{path.relative_to(ROOT)}: Python cell {index}: {error}')
    # Exclude literal code and keep the one explicit table of legacy aliases.
    prose = re.sub(r'(?ms)^----\n.*?^----', '', text)
    if path.name != 'notation.adoc':
        for retired in ('V_h', 'V_r'):
            if re.search(r'\b'+retired+r'\b', prose):
                failures.append(f'{path.relative_to(ROOT)}: retired space symbol {retired}')
    if re.search(r'\\(?:inD|toD)|D_\\mu_\{', prose):
        failures.append(f'{path.relative_to(ROOT)}: malformed parameter-domain notation')

contracts = {
    'materials/modules/ROOT/pages/notation.adoc':
        ('X^{\\mathcal N}', 'X_N', 'N_q', 'L_i', '\\mathbb B_M', 'GW=H^T'),
    'materials/modules/ROOT/pages/assimilation/geim.adoc':
        ('I_M^L', '\\rho_j', '\\gamma_j', 'L_i', '\\mathbb B_M', 'G\\mathbf w_s=h_s'),
    'materials/modules/ROOT/pages/assimilation/variational.adoc':
        ('GW=H^T', 'Hu=W^TGu', '\\widehat u=Za+Wd'),
    'docs/modules/ROOT/pages/labs/session08-geim.adoc':
        ('rho=', 'B_geim=H@rho', 'reconstruct=lambda y: rho@np.linalg.solve(B_geim,y)'),
}
for name, required in contracts.items():
    source = (ROOT/name).read_text()
    for token in required:
        if token not in source:
            failures.append(f'{name}: missing interface definition {token}')
if failures:
    raise SystemExit('\n'.join(failures))
print(f'Notation contract checked across {len(files)} active notes/practicals; Python cells parse.')
