(fn CombatStep (Dt Dist)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) Dist 1500.0)
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) Dist 110.0)
        (:then
          (Funzionedichiamata|ChaseFoe :Dt Dt))
        (:else
          (Funzionedichiamata|FaceToward :Goal (Trasformazione|GetActorLocation (Variabili|Predefinito|OttieniFoe)))
          (Funzionedichiamata|Bite :Dt Dt)
          (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniChasing)
            (:then
              (Variabili|Predefinito|ImpostaChasing "false")
              (Componenti|Animazione|PlayAnimation (Variabili|Predefinito|OttieniMesh) "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle" "true"))))))))
