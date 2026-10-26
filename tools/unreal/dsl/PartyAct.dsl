(fn PartyAct (Dt)
  (Funzionedichiamata|Separate :Dt Dt)
  (Variabili|Predefinito|ImpostaNStamina (Matematica|Float|Min(Float) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniNStamina) Dt) (Variabili|Predefinito|OttieniNPool)))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Matematica|Float|Max(Float) (Variabili|Predefinito|OttieniStunUntil) (Variabili|Predefinito|OttieniKnockUntil)) (Utilità|Testo|GetGameTimeinSeconds))
    (:then
      (Funzionedichiamata|StopMoving))
    (:else
      (Funzionedichiamata|Recover)
      (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniControlled)
        (:then
          (Funzionedichiamata|ControlledAct :Dt Dt))
        (:else
          (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniTarget))
            (:then
              (Funzionedichiamata|PartyFight :Dt Dt))
            (:else
              (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniHold)
                (:then
                  (Funzionedichiamata|StopMoving))
                (:else
                  (Funzionedichiamata|FollowLeader :Dt Dt))))))))))
