(fn PreferTarget (Reach)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniHeroTarget))
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Trasformazione|GetDistanceTo (Gioco|GetPlayerPawn 0) (Variabili|Predefinito|OttieniHeroTarget)) Reach)
        (:then
          (Variabili|Predefinito|ImpostaBestTarget (Variabili|Predefinito|OttieniHeroTarget)))))))
