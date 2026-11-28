;; Static locations in the Atomspace; prop availability is scheduled separately.
(room hallway)
(room kitchen)
(room living-room)
(room bedroom)
(place kitchen-table kitchen)
(place glass kitchen-table)
(place food-bowl kitchen)
(place litter-box hallway)
(place zip-tie kitchen)
(place cardboard-box living-room)
(place catnip-mouse bedroom)
(place paper-bag living-room)
(place candle kitchen)
(resident tater-tot)
(resident paxton)

;; Every room opens onto the hallway. An action can take one travel tick.
(= (nextRoom $from $to) (if (== $from hallway) $to hallway))
(= (roomAt 0) hallway)
(= (roomAt 1) kitchen)
(= (roomAt 2) living-room)
(= (roomAt 3) bedroom)

;; Advance a seeded random stream exactly once per tick, regardless of action.
(= (nextRandom $rng) (% (+ (* 1664525 $rng) 1013904223) 4294967296))
(= (humanRoom $step $rng $old)
    (if (== (% (- $step 1) 7) 0) (roomAt (% (floor-math (/ $rng 65536)) 4)) $old))
