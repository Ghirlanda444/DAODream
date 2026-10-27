(fn TryUnlock2 (Box)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniGBool) (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Classe|BPContainer|OttieniKeyReq Box)) (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniPLockpick) 0.0)) (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniPLockpick) (Classe|BPContainer|OttieniLockLevel Box))))
    (:then
      (Classe|BPContainer|Unlock Box)
      (Funzionedichiamata|ShowMsg :Txt "Unlocked")
      (Funzionedichiamata|ShowLoot :Box Box))
    (:else
      (Funzionedichiamata|ShowMsg :Txt (Utilità|Stringa|SelectString "Locked: it needs its key" "Locked: you have not the skill to pick it" (Classe|BPContainer|OttieniKeyReq Box))))))
