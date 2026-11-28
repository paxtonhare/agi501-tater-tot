;; The schedule gates the menu; ordinary toy rules apply once it appears.
(= (taskGoal paper-bag) curiosity)
(= (taskRoom paper-bag $_) (toyRoom paper-bag))
(= (duration paper-bag) 3)
(= (propVisible $tick $arrival) (and (> $arrival 0) (>= $tick $arrival)))
(= (bagMenu $visible $room $human ($h $c $a $m $t $l) ($zip $box $mouse $bag) $menu)
    (if $visible (append $menu ((toyCandidate paper-bag $room $human $c $bag))) $menu))
