(fn ToggleSustained ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTUntil) (Variabili|Predefinito|OttieniTSlot)) 0.0)
    (:then
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniTUntil) (Variabili|Predefinito|OttieniTSlot) 0.0)
      (Variabili|Predefinito|ImpostaPPool (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniPPool) (Variabili|Predefinito|OttieniTUpkeep)))
      (Variabili|Predefinito|ImpostaPFatigue (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniPFatigue) (Variabili|Predefinito|OttieniTFatigue)))
      (Funzionedichiamata|AfterTalent :Txt (Utilità|Stringa|Append (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) (Variabili|Predefinito|OttieniTSlot)) " off")))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniPPool) (Variabili|Predefinito|OttieniTUpkeep)) 0.0)
        (:then
          (Funzionedichiamata|ShowMsg :Txt "Not enough stamina"))
        (:else
          (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniTUntil) (Variabili|Predefinito|OttieniTSlot) 1000000000.0)
          (Variabili|Predefinito|ImpostaPPool (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniPPool) (Variabili|Predefinito|OttieniTUpkeep)))
          (Variabili|Predefinito|ImpostaPStamina (Matematica|Float|Min(Float) (Variabili|Predefinito|OttieniPStamina) (Variabili|Predefinito|OttieniPPool)))
          (Variabili|Predefinito|ImpostaPFatigue (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniPFatigue) (Variabili|Predefinito|OttieniTFatigue)))
          (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniTReady) (Variabili|Predefinito|OttieniTSlot) (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) (Variabili|Predefinito|OttieniTCool)))
          (Funzionedichiamata|AfterTalent :Txt (Utilità|Stringa|Append (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) (Variabili|Predefinito|OttieniTSlot)) " on")))))))
