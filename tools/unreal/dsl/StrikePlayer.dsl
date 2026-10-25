(fn StrikePlayer (Attacker Atk DmgMin DmgMax Scale Crit Pen Bonus Flank)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniTalking) (Variabili|Predefinito|OttieniGameOver)) (Variabili|Predefinito|OttieniPlayerDown)) (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 100.0) (Variabili|Predefinito|OttieniPDisplace)))
    (:else
      (Funzionedichiamata|FlankBonus :Attacker Attacker :Target (Gioco|GetPlayerPawn 0) :Most Flank)
      (Funzionedichiamata|ResolveHit :Atk Atk :Def (Variabili|Predefinito|OttieniPDef) :DmgMin DmgMin :DmgMax DmgMax :Scale Scale :Crit Crit :Pen Pen :Bonus Bonus :Armour (Variabili|Predefinito|OttieniPArmour))
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniLastDamage) 0.0)
        (:then
          (Funzionedichiamata|HurtPlayer :Amount (Variabili|Predefinito|OttieniLastDamage)))))))
