(fn HeroUseStep (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Trasformazione|GetDistanceTo (Gioco|GetPlayerPawn 0) (Variabili|Predefinito|OttieniHeroUse)) 200.0)
    (:then
      (Funzionedichiamata|HeroWalk :Goal (Trasformazione|GetActorLocation (Variabili|Predefinito|OttieniHeroUse)) :Dt Dt))
    (:else
      (Funzionedichiamata|HeroUseNow))))
