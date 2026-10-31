set -e
cd /home/user
python3 -I scripts/build_excel.py
rm -rf /tmp/recalc && mkdir -p /tmp/recalc
cd /tmp/recalc && timeout 300 soffice --headless --calc --convert-to xlsx --outdir /tmp/recalc /home/user/entrega_semana8/NFL_2026_S8_matchups.xlsx >/dev/null 2>&1
cd /home/user
python3 -I scripts/build_json.py
python3 -I scripts/verify.py
