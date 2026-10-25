(fn CombatRound ()
  (Funzionedichiamata|ChooseTactic)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniTacSlot) 0)
    (:then
      (Funzionedichiamata|DoTalent))
    (:else
      (Funzionedichiamata|StrikeFoe))))
