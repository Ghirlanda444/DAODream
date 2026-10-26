(fn HeroAIAct ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniHeroTarget))
    (:then
      (Funzionedichiamata|HeroReach)
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Trasformazione|GetDistanceTo (Gioco|GetPlayerPawn 0) (Variabili|Predefinito|OttieniHeroTarget)) (Variabili|Predefinito|OttieniPickDist))
        (:then
          (IA|Navigazione|SimpleMovetoActor (Gioco|GetPlayerController 0) :Goal (Variabili|Predefinito|OttieniHeroTarget)))
        (:else
          (IA|Navigazione|StopMovement (Gioco|GetPlayerController 0))
          (Funzionedichiamata|HeroStrike))))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Trasformazione|GetDistanceTo (Gioco|GetPlayerPawn 0) (Variabili|Predefinito|OttieniSelected)) 350.0)
        (:then
          (IA|Navigazione|SimpleMovetoActor (Gioco|GetPlayerController 0) :Goal (Variabili|Predefinito|OttieniSelected)))
        (:else
          (IA|Navigazione|StopMovement (Gioco|GetPlayerController 0)))))))
