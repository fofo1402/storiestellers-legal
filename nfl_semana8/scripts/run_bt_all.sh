set -e
cd /home/user
for s in bt2_build bt3_build bt4_build bt5_build bt6_build bt7_build; do echo "== $s $(date +%T)"; python3 -I scripts/$s.py; done
echo "== FIN $(date +%T)"
