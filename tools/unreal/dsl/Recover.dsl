(fn Recover ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniKnocked)
    (:then
      (Variabili|Predefinito|ImpostaKnocked "false")
      (Componenti|Animazione|PlayAnimation (Variabili|Predefinito|OttieniMesh) "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle" "true"))))
