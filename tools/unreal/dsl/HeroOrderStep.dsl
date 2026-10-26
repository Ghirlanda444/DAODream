(fn HeroOrderStep (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniHeroTarget))
    (:then
      (Funzionedichiamata|HeroAttackStep :Dt Dt))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniHeroUse))
        (:then
          (Funzionedichiamata|HeroUseStep :Dt Dt))
        (:else
          (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniMoving)
            (:then
              (Funzionedichiamata|HeroMoveStep :Dt Dt))))))))
