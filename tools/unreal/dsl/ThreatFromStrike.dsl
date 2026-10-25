(fn ThreatFromStrike (Attacker Damage)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniHostile) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDead)))
    (:then
      (Funzionedichiamata|AttackedBy :Who Attacker)
      (Funzionedichiamata|DamageThreat :Who Attacker :Damage Damage))))
