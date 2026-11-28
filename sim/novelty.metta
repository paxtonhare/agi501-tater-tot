;; Ablate the candidate's gNovel input, not gCurio, toy boredom, or the
;; novelty observation used by OpenPSI to appraise changes in the world.
(= (noveltyMenu on $menu) $menu)
(= (noveltyMenu off $menu)
    (collapse (let (action $id ($i $tr $h $c $_ $s $e $so) $risk $delta) (superpose $menu)
        (action $id ($i $tr $h $c 0 $s $e $so) $risk $delta))))
