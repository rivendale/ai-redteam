#!/usr/bin/env bash
# Committed with the failures the reviews of #121 found; they must hold for every later change to the cases or the scorer.
# Hand-made probe reports for #121's case-09, case-10 and case-03 (from the two reviews). A probe "passes" when the case
# scores it clean (found, no violation); each must match its expectation.
P=$(cd "$(dirname "$0")" && pwd); R=$(cd "$P/../../.." && pwd); S=${SCORE:-$R/evals/score.py}; C=${CASES:-$R/evals/review-practice/cases}
bad=0
for d in "$P"/p*/; do n=$(basename "$d"); read case want <<<"$(python3 -c "import json;e=json.load(open('$P/expect.json'))['$n'];print(e[0], 'pass' if e[1] else 'fail')")"
  o=$(python3 "$S" --cases "$C" --reports "$d" --only "$case" 2>&1 | grep "^$case")
  viol=$(awk '{print $NF}' <<<"$o"); rec=$(grep -oE " [0-9]+/[0-9]+ " <<<"$o" | head -1 | tr -d ' ')
  got=fail; { [ "$viol" = 0 ] && { [ -z "$rec" ] || [ "${rec%/*}" = "${rec#*/}" ] || [ "$rec" = "-" ]; }; } && got=pass
  [ "$got" = "$want" ] && echo "ok   $n ($got)" || { echo "FAIL $n: want $want, got $got | $o" | cut -c1-200; bad=$((bad+1)); }
done
echo "probes: $bad wrong"; exit $((bad>0))
