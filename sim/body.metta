;; Sleep and litter world rules. The post-meal clock is separate from the drives.
;; Removing sleep means no tiredness contribution to appraisal or the menu.
(= (napLevels on $drives) $drives)
(= (napLevels off ($h $c $a $m $_ $l)) ($h $c $a $m 0 $l))
(= (napMenu on $menu) $menu)
(= (napMenu off $menu)
    (collapse (let $candidate (superpose $menu)
        (if (== (actionId $candidate) sleep) (empty) $candidate))))

(= (riseTiredness $tiredness) (min 100 (+ $tiredness 2)))
(= (riseLitter $litter $afterMeal)
    (min 100 (+ $litter (if (> $afterMeal 0) 8 3))))
(= (mealClock $action $work $afterMeal)
    (if (and (== $action eat) (== $work 0)) 5 (max 0 (- $afterMeal 1))))

(= (taskGoal sleep) tiredness)
(= (taskGoal use-litter) litter)
(= (taskRoom sleep $_) bedroom)
(= (taskRoom use-litter $_) (match &self (place litter-box $room) $room))
(= (duration sleep) 6)
(= (duration use-litter) 2)
(= (relieve tiredness ($h $c $a $m $t $l)) ($h $c $a $m 0 $l))
(= (relieve litter ($h $c $a $m $t $l)) ($h $c $a $m $t 0))
