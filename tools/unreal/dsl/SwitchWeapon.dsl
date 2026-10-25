(fn SwitchWeapon ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniTalking) (Utility|Operatori|Minoreuguale(<=) (Variabili|Predefinito|OttieniBowRange) 0.0))
    (:else
      (Variabili|Predefinito|ImpostaBowOn (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniBowOn)))
      (Variabili|Predefinito|ImpostaPBaseInterval (Matematica|Float|SelectFloat (Variabili|Predefinito|OttieniBowInterval) (Variabili|Predefinito|OttieniPMeleeInterval) (Variabili|Predefinito|OttieniBowOn)))
      (Funzionedichiamata|SumOwn)
      (Funzionedichiamata|ShowMsg :Txt (Utilità|Stringa|SelectString "Shortbow" "Sword and shield" (Variabili|Predefinito|OttieniBowOn))))))
