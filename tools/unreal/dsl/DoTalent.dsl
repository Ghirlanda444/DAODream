(fn DoTalent ()
  (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniNReady) (Variabili|Predefinito|OttieniTacSlot) (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniTacSlot) 18) 3))))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniTacSlot) 18) 1)) 2.0)
    (:then
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniNOn) (Variabili|Predefinito|OttieniTacSlot) 1.0)
      (Variabili|Predefinito|ImpostaNPool (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniNPool) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniTacSlot) 18) 4))))
      (Variabili|Predefinito|ImpostaNStamina (Matematica|Float|Min(Float) (Variabili|Predefinito|OttieniNStamina) (Variabili|Predefinito|OttieniNPool)))
      (Variabili|Predefinito|ImpostaNFatigue (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniNFatigue) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniTacSlot) 18) 5))))
      (Funzionedichiamata|NSumOwn)
      (Funzionedichiamata|SayTalent))
    (:else
      (Variabili|Predefinito|ImpostaNStamina (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniNStamina) (Variabili|Predefinito|OttieniNCostNow)))
      (Funzionedichiamata|SayTalent)
      (Funzionedichiamata|TalentEffect :K (Variabili|Predefinito|OttieniTacSlot)))))
