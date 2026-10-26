(fn BleedTick (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniBleedUntil) (Utilità|Testo|GetGameTimeinSeconds))
    (:then
      (Funzionedichiamata|TakeHit :Damage (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniBleedRate) Dt)))))
