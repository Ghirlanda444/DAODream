(fn StrikePlayer (Attacker Atk DmgMin DmgMax Scale Crit Pen Bonus Flank)
  (Variabili|Predefinito|ImpostaLastDamage -1.0)
  (Funzionedichiamata|AttackerState :Attacker Attacker)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniTalking) (Variabili|Predefinito|OttieniGameOver)) (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniPlayerDown) (Variabili|Predefinito|OttieniAStunned))) (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 100.0) (Variabili|Predefinito|OttieniPDisplace)))
    (:else
      (Funzionedichiamata|FlankBonus :Attacker Attacker :Target (Gioco|GetPlayerPawn 0) :Most Flank)
      (Funzionedichiamata|ResolveHit :Atk (Utility|Operatori|Sottrai Atk (Variabili|Predefinito|OttieniAPen)) :Def (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniPDef) (Matematica|Float|SelectFloat (Variabili|Predefinito|OttieniPMissile) 0.0 (Variabili|Predefinito|OttieniARanged))) :DmgMin DmgMin :DmgMax DmgMax :Scale Scale :Crit Crit :Pen Pen :Bonus Bonus :Armour (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniPArmour) (Matematica|Float|SelectFloat (Variabili|Predefinito|OttieniPArmourAdd) 0.0 (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniPArmourUntil) (Utilità|Testo|GetGameTimeinSeconds)))))
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniLastDamage) 0.0)
        (:then
          (Funzionedichiamata|HurtPlayer :Amount (Variabili|Predefinito|OttieniLastDamage)))))))
