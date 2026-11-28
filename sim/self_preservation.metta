;; Apply to candidates that can cost health (currently only inspect-candle).
;; Missing health adds lasting perceived risk, separate from fear and recall.
(= (injuryAdjustedRisk off $_ $risk) $risk)
(= (injuryAdjustedRisk on $health $risk) (min 1 (+ $risk (/ (- 100 $health) 100))))
