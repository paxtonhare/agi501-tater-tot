;; Heat is immediate. A first in-room tick is a sniff; a second consecutive
;; work tick gets close enough to singe. Fear fades; recalled risk does not.
(= (taskGoal inspect-candle) curiosity)
(= (taskRoom inspect-candle $_) (match &self (place candle $room) $room))
(= (duration inspect-candle) 2)
(= (candleMemoryRisk off $_) 0)
(= (candleMemoryRisk on $space)
    (* 0.26 (min 3 (catEventCount $space singe inspect-candle))))
(= (candleRisk $memory $space $fear)
    (min 1 (+ 0.14 (+ (/ $fear 200) (candleMemoryRisk $memory $space)))))
(= (candleMenu $visible $room $human ($h $c $a $m $t $l) $risk $menu)
    (if $visible
        (let $interest (* (/ $c 100) (reachWeight inspect-candle $room $human))
            (append $menu ((catAction inspect-candle (0 0 0 $interest $interest (* 0.30 $interest) 0 0)
                                      $risk (0 0.005 0 0 0 0 0 0)))))
        $menu))

;; Returns the physical verb to log and the new health/fear meters.
(= (candleOutcome $action $work ($health $fear))
    (if (and (== $action inspect-candle) (== $work 0))
        (candle-singed (max 0 (- $health 20)) 100)
        ($action $health (max 0 (- $fear 10)))))
(= (recordSinge $space $tick $action $room $human)
    (if (== $action candle-singed)
        (rememberCatEvent $space $tick singe inspect-candle (== $room $human))
        true))
