(fn HeroStrike ()
  (bind (_x _y _z) (Matematica|Vettore|BreakVector (Utility|Operatori|Sottrai (Trasformazione|GetActorLocation (Variabili|Predefinito|OttieniHeroTarget)) (Trasformazione|GetActorLocation (Gioco|GetPlayerPawn 0)))))
  (Trasformazione|SetActorRotation (Gioco|GetPlayerPawn 0) (Matematica|Rotatore|MakeRotator 0.0 0.0 (Matematica|Trig|Atan2(Degrees) _y _x)) "false")
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Utility|Operatori|Sottrai (Utilità|Testo|GetGameTimeinSeconds) (Variabili|Predefinito|OttieniLastAttack)) (Variabili|Predefinito|OttieniPInterval))
    (:else
      (Funzionedichiamata|PlayerAttackNow))))
