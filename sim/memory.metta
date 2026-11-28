;; Separate named Atomspace in PeTTa v1.0.2; clear it before each run.
(= (clearCatEvents $space)
    (collapse (let $event (match $space (cat-event $t $kind $action $present)
                                       (cat-event $t $kind $action $present))
        (remove-atom $space $event))))
(= (rememberCatEvent $space $tick $kind $action $humanPresent)
    (add-atom $space (cat-event $tick $kind $action $humanPresent)))
(= (catEventCount $space $kind $action)
    (size-atom (collapse (match $space (cat-event $tick $kind $action $_) $tick))))

;; Let MAGUS weigh the extra risk. Cap the count at four to bound the effect.
;; Memory-off still records the events; it does not use them in decision making.
(= (recallScoldingRisk off $_ $_) 0)
(= (recallScoldingRisk on $space $human)
    (* (min 4 (catEventCount $space scolding knock))
       (if (== $human kitchen) 0.18 0.06)))
(= (recordScolding $space $tick $action $room $human)
    (if (== $action knock-scolded)
        (rememberCatEvent $space $tick scolding knock (== $room $human))
        true))
