;; Bypass only MetaMo's goal-update damping hook. Keep its other checks,
;; conservative fallback, boundary caution, projection and state blending.
(= (undampedDelta $_ $delta) $delta)
(= (catBimonad on) (defaultMetaMoBimonad))
(= (catBimonad off)
    (let (metaMoPseudoBimonad $appraise $decide $_ $boundary $project $contractive $safe)
         (defaultMetaMoBimonad)
         (metaMoPseudoBimonad $appraise $decide undampedDelta $boundary $project $contractive $safe)))
