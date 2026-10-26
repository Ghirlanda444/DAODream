(fn HeroRepath (Goal Dt)
  (Variabili|Predefinito|ImpostaPathTimer (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniPathTimer) Dt))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniPathTimer) 0.0)
    (:else
      (Variabili|Predefinito|ImpostaPathTimer 0.4)
      (Variabili|Predefinito|ImpostaHeroPath (Classe|NavigationPath|OttieniPathPoints (IA|Navigazione|FindPathtoLocationSynchronously :PathStart (Trasformazione|GetActorLocation (Gioco|GetPlayerPawn 0)) :PathEnd Goal))))))
