(fn HeroTick (Dt)
  (Funzionedichiamata|MayAttackTick)
  (Funzionedichiamata|PlayerBleedTick :Dt Dt)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniTalking) (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniPlayerDown) (Variabili|Predefinito|OttieniGameOver)))
    (:then
      (Variabili|Predefinito|ImpostaHeroTarget)
      (Variabili|Predefinito|ImpostaHeroUse)
      (Variabili|Predefinito|ImpostaMoving "false"))
    (:else
      (Funzionedichiamata|KeepCursor)
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniSelected))
        (:then
          (Funzionedichiamata|HeroAI :Dt Dt))
        (:else
          (Funzionedichiamata|HeroOrderStep :Dt Dt))))))
