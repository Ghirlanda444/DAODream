(fn CommandNpc (Where)
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPDlgNPC|OttieniHostile (Variabili|Predefinito|OttieniPickNpc))
    (:then
      (Variabili|Predefinito|ImpostaHeroTarget (Variabili|Predefinito|OttieniPickNpc))
      (Funzionedichiamata|ShowMsg :Txt (Utilità|Stringa|Append "Attack: " (Classe|BPDlgNPC|OttieniDisplayName (Variabili|Predefinito|OttieniPickNpc)))))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Classe|BPDlgNPC|OttieniInParty (Variabili|Predefinito|OttieniPickNpc))
        (:then
          (Variabili|Predefinito|ImpostaMoveGoal Where)
          (Variabili|Predefinito|ImpostaMoving "true"))
        (:else
          (Variabili|Predefinito|ImpostaHeroUse (Variabili|Predefinito|OttieniPickNpc)))))))
