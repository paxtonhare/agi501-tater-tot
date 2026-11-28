;; Optional short-term feedback, separate from MetaMo's motivational state.
;; (attended-task attention rewarded-task reward), both strengths in [0, 1].
(= (initialFeedback) (none 0 none 0))

;; First work on a task captures attention; repeats don't refresh it. Travel
;; toward the same task keeps the decaying trace, but a replan drops it.
(= (nextAttention $task $verb $attended $strength)
    (if (== $task $attended) ($attended (* 0.8 $strength))
        (if (== $verb move) (none 0) ($task 1))))

;; Reward actual relief, not merely choosing a task or taking a step toward it.
(= (driveRelief ($h $c $a $m $t $l) ($nh $nc $na $nm $nt $nl))
    (/ (+ (+ (- $h $nh) (- $c $nc))
          (+ (+ (- $a $na) (- $m $nm)) (+ (- $t $nt) (- $l $nl)))) 100))
(= (updateCatFeedback $task $verb $before $after ($attended $attention $rewarded $reward))
    (let* ((($focus $share) (nextAttention $task $verb $attended $attention))
           ($relief (driveRelief $before $after)))
        (if (> $relief 0) ($focus $share $task $relief)
            ($focus $share $rewarded (* 0.65 $reward)))))

;; The reward boosts the task's existing goal correlations, i.e. how well the
;; action serves each goal. Switching discounts those correlations (less
;; payoff after reorienting), without conflating effort with physical danger.
;; MAGUS still scores every candidate, using its usual appraisal and damping.
(= (feedbackCorrelation $value $factor) (min 1 (* $value $factor)))
(= (feedbackCorrelations ($i $tr $h $c $n $s $e $so) $factor)
    ((feedbackCorrelation $i $factor) (feedbackCorrelation $tr $factor)
     (feedbackCorrelation $h $factor) (feedbackCorrelation $c $factor)
     (feedbackCorrelation $n $factor) (feedbackCorrelation $s $factor)
     (feedbackCorrelation $e $factor) (feedbackCorrelation $so $factor)))
(= (applyCatFeedback $menu ($attended $attention $rewarded $reward))
    (if (== $menu ()) ()
        (let* ((((action $id $corr $risk $delta) $tail) (decons $menu))
               ($bonus (if (== $id $rewarded) (* 0.5 $reward) 0))
               ($cost (if (== $id $attended) 0 (* 0.22 $attention)))
               ($factor (* (+ 1 $bonus) (- 1 $cost)))
               ($newCorr (if (== $factor 1) $corr (feedbackCorrelations $corr $factor))))
            (cons-atom (action $id $newCorr $risk $delta)
                       (applyCatFeedback $tail ($attended $attention $rewarded $reward))))))
