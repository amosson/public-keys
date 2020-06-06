py3 << EOF
import sys
sys.path.append('src')
EOF

let test#python#pytest#executable = 'PYTHONPATH=src pytest --pdb'
let test#python#runner = 'pytest'

let g:deoplete#sources#jedi#extra_path = $PYTHONPATH
