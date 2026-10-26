(fn StrikeFoe ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniStaff)
    (:then
      (Funzionedichiamata|ShootFx)
      (Funzionedichiamata|SpellHitFoe :Amount (Matematica|Casuale|RandomFloatinRange (Variabili|Predefinito|OttieniDmgMin) (Variabili|Predefinito|OttieniDmgMax))))
    (:else
      (Funzionedichiamata|HitFoe :Bonus 0.0 :Mul 1.0 :bOff "false" :bSure "false"))))
