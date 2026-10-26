(fn HeroAttackStep (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPDlgNPC|OttieniDead (Variabili|Predefinito|OttieniHeroTarget))
    (:then
      (Variabili|Predefinito|ImpostaHeroTarget))
    (:else
      (Funzionedichiamata|HeroReach)
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Trasformazione|GetDistanceTo (Gioco|GetPlayerPawn 0) (Variabili|Predefinito|OttieniHeroTarget)) (Variabili|Predefinito|OttieniPickDist))
        (:then
          (Funzionedichiamata|HeroWalk :Goal (Trasformazione|GetActorLocation (Variabili|Predefinito|OttieniHeroTarget)) :Dt Dt))
        (:else
          (Funzionedichiamata|HeroStrike))))))
