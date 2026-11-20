#!/bin/bash
# يحفظ الحالة بعد التحديث (التواريخ في build.py + sec_state + بيانات ثاندر) في فرع rayl-tools
set -e
T="$(cd "$(dirname "$0")" && pwd)"
for d in /home/claude/sec1120*/; do n=$(basename $d); cp $d/build.py $d/info.py $d/fv.json "$T/home/$n/"; done
cp /home/claude/sec_state.json /home/claude/sec_weekly.py /home/claude/secfetch_gen.py /home/claude/secday1120.json "$T/home/"
cp /home/claude/thndr/* "$T/home/thndr/"
cd "$T" && git add -A && git commit -qm "حفظ حالة تقارير القطاعات $(date +%F)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016z8xLKiXRpNtu7he7XPkGg" && git push -q origin HEAD:rayl-tools && echo SAVED
